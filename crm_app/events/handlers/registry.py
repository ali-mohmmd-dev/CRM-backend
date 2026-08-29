from __future__ import annotations

from collections.abc import Callable

from . import customers, leads, works

Handler = Callable[[dict], None]

_REGISTRY: dict[str, Handler] = {}


def register_handlers() -> dict[str, Handler]:
    _REGISTRY.clear()
    for module in (leads, customers, works):
        _REGISTRY.update(module.HANDLERS)
    return _REGISTRY


def get_handler(event_type: str) -> Handler | None:
    if not _REGISTRY:
        register_handlers()
    return _REGISTRY.get(event_type)


def dispatch(envelope: dict) -> None:
    event_type = envelope.get('event_type')
    if not event_type:
        raise ValueError('Envelope missing event_type')
    handler = get_handler(event_type)
    if handler is None:
        raise KeyError(f'No handler registered for event_type={event_type}')
    handler(envelope)
