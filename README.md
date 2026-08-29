# SaaS CRM Backend

Multi-tenant CRM API built with Django REST Framework and a Kafka (Redpanda) event bus.

## Stack

- Django 6 + Django REST Framework + SimpleJWT
- OpenAPI via drf-spectacular (`/api/schema/swagger-ui/`)
- Kafka events via `confluent-kafka` (local broker: Redpanda)

## Project layout

| Package | Role |
|---------|------|
| `core/` | Django **project** (settings, root urls, wsgi/asgi) — not a domain app |
| `accounts/` | Organization, User, register / token / me |
| `staff/` | Staff CRUD |
| `works/` | Work CRUD + work domain events |
| `customers/` | Customer CRUD + follow-up event |
| `leads/` | Lead CRUD + mark-called / convert events |
| `dashboard/` | Stats, activity, calendar |
| `events/` | Kafka producer, consumer, handlers |
| `common/` | Shared `OrganizationOwnedModel`, scoped viewsets, `publish_after_commit` |

Public API paths are unchanged (`/api/staff/`, `/api/works/`, `/api/customers/`, `/api/leads/`, `/api/dashboard/...`, `/api/register/`, etc.).

## Prerequisites

- Python 3.12+
- Docker Desktop (for Redpanda) — start it before bootstrap if you want Kafka up immediately
- Virtualenv (created by bootstrap)

## 1. Setup (bootstrap)

Start **Docker Desktop**, then from the repo root run **one** of these:

**Command Prompt (cmd):**

```cmd
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1
```

**PowerShell:**

```powershell
.\scripts\bootstrap.ps1
```

Do **not** double-click `bootstrap.ps1`, and do not run bare `.\scripts\bootstrap.ps1` from cmd if it opens Notepad — that means Windows opened the file instead of executing it. Use the `powershell -File ...` form above.

### What bootstrap does

1. Checks Python and Docker are on PATH  
2. Creates `venv/` if missing  
3. Installs `requirements.txt`  
4. Copies `.env.example` → `.env` if `.env` is missing  
5. Runs `manage.py migrate`  
6. Runs `docker compose up -d` (Redpanda)  
7. Runs `manage.py check`  
8. Prints next steps  

### How you know bootstrap worked

Look for either:

```text
Bootstrap complete.
```

or (Django OK, Kafka not started — usually Docker Desktop was off):

```text
Bootstrap finished with warnings (Redpanda not started).
```

You should also see:

```text
System check identified no issues (0 silenced).
```

Quick re-check:

```cmd
.\venv\Scripts\python.exe manage.py check
```

If you previously used old app labels (`core` / `crm_app`), delete `db.sqlite3` and run bootstrap (or migrate) again.

## 2. Create Kafka topics (once per fresh Redpanda)

After Redpanda is running, create the topics the consumer expects:

```cmd
docker compose up -d
docker compose exec redpanda rpk topic create crm.lead.events crm.customer.events crm.work.events
```

List them:

```cmd
docker compose exec redpanda rpk topic list
```

Without this step, `consume_events` often logs:

```text
UNKNOWN_TOPIC_OR_PART ... crm.lead.events
```

## 3. Run the app (two terminals)

**Terminal 1 — API**

```cmd
.\venv\Scripts\activate.bat
python manage.py runserver
```

**Terminal 2 — event consumer**

```cmd
.\venv\Scripts\activate.bat
python manage.py consume_events
```

(PowerShell: use `.\venv\Scripts\Activate.ps1` instead of `activate.bat`.)

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/ | API |
| http://127.0.0.1:8000/api/schema/swagger-ui/ | Swagger UI |
| `localhost:9092` | Kafka / Redpanda bootstrap |

`runserver` alone is enough for CRUD. `consume_events` is required for async side effects (for example converting a lead to a customer).

## Environment

| Variable | Default |
|----------|---------|
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` |
| `KAFKA_CLIENT_ID` | `crm-backend` |
| `KAFKA_CONSUMER_GROUP` | `crm-backend-handlers` |

Defaults live in `core/settings.py` via `os.environ.get`. `.env` is for reference; set variables in your shell if you need overrides (no dotenv loader in settings).

`DJANGO_SETTINGS_MODULE` is `core.settings`.

## Important API note

`POST /api/leads/{id}/convert-to-customer/` returns **202** with the **converted lead**. The customer is created asynchronously by the Kafka `LeadConverted` handler when `consume_events` is running and Redpanda topics exist. Refresh the customers list after convert.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `bootstrap.ps1` opens Notepad | Run `powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1` |
| Bootstrap warns about docker compose | Start Docker Desktop, then `docker compose up -d` |
| `UNKNOWN_TOPIC_OR_PART` in consume_events | Create topics (step 2 above) |
| Convert lead returns 202 but no customer | Start Redpanda + `consume_events`; create topics |

## Tests

```cmd
.\venv\Scripts\activate.bat
python manage.py test accounts leads events
```

## More documentation

See [docs/EVENTS.md](docs/EVENTS.md) for Kafka architecture, topics, envelopes, and how to add events.
