from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


def build_envelope(
    event_type: str,
    organization_id: int,
    payload: dict[str, Any],
    *,
    event_id: str | None = None,
    occurred_at: str | None = None,
) -> dict[str, Any]:
    return {
        'event_id': event_id or str(uuid.uuid4()),
        'event_type': event_type,
        'occurred_at': occurred_at or datetime.now(timezone.utc).isoformat(),
        'organization_id': organization_id,
        'payload': payload,
    }
