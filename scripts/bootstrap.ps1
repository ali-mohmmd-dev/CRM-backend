# Bootstrap CRM backend (Windows PowerShell).
# Run from repo root: .\scripts\bootstrap.ps1

$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> Bootstrapping CRM backend from $Root" -ForegroundColor Cyan

function Require-Command {
    param([string]$Name, [string]$Hint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Error "$Name not found. $Hint"
        exit 1
    }
}

Require-Command -Name 'python' -Hint 'Install Python 3.12+ and ensure it is on PATH.'
Require-Command -Name 'docker' -Hint 'Install Docker Desktop and ensure docker is on PATH.'

$PythonVersion = & python --version 2>&1
Write-Host "    Python: $PythonVersion"

$VenvPython = Join-Path $Root 'venv\Scripts\python.exe'
$VenvPip = Join-Path $Root 'venv\Scripts\pip.exe'

if (-not (Test-Path $VenvPython)) {
    Write-Host '==> Creating venv/' -ForegroundColor Cyan
    & python -m venv venv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host '==> venv/ already exists' -ForegroundColor DarkGray
}

Write-Host '==> Installing dependencies' -ForegroundColor Cyan
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $VenvPip install -r (Join-Path $Root 'requirements.txt')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$EnvExample = Join-Path $Root '.env.example'
$EnvFile = Join-Path $Root '.env'
if ((Test-Path $EnvExample) -and -not (Test-Path $EnvFile)) {
    Write-Host '==> Creating .env from .env.example' -ForegroundColor Cyan
    Copy-Item $EnvExample $EnvFile
} elseif (Test-Path $EnvFile) {
    Write-Host '==> .env already exists (left unchanged)' -ForegroundColor DarkGray
}

Write-Host '==> Running migrations' -ForegroundColor Cyan
& $VenvPython manage.py migrate
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host '==> Starting Redpanda (docker compose up -d)' -ForegroundColor Cyan
& docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Warning 'docker compose up -d failed. Is Docker Desktop running? Continuing bootstrap; start Docker and re-run this step before consume_events.'
    $script:DockerComposeFailed = $true
} else {
    $script:DockerComposeFailed = $false
}

Write-Host '==> Django system check' -ForegroundColor Cyan
& $VenvPython manage.py check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ''
if ($script:DockerComposeFailed) {
    Write-Host 'Bootstrap finished with warnings (Redpanda not started).' -ForegroundColor Yellow
} else {
    Write-Host 'Bootstrap complete.' -ForegroundColor Green
}
Write-Host ''
Write-Host 'Next steps (activate venv, then run two processes):' -ForegroundColor Cyan
Write-Host '  .\venv\Scripts\Activate.ps1'
Write-Host '  python manage.py runserver'
Write-Host '  python manage.py consume_events'
Write-Host ''
Write-Host 'Swagger: http://127.0.0.1:8000/api/schema/swagger-ui/'
Write-Host 'Kafka bootstrap (default): localhost:9092'
Write-Host ''
Write-Host 'Note: .env is optional. Settings already default Kafka to localhost:9092.'
Write-Host '      To override, set env vars in your shell before starting processes.'
if ($script:DockerComposeFailed) {
    Write-Host '      Start Docker Desktop, then: docker compose up -d'
}
