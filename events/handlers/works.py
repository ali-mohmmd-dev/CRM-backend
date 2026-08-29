import logging

from ..types import EventNames

logger = logging.getLogger(__name__)


def handle_work_created(envelope: dict) -> None:
    payload = envelope['payload']
    logger.info(
        'WorkCreated work_id=%s organization_id=%s status=%s',
        payload.get('work_id'),
        envelope.get('organization_id'),
        payload.get('status'),
    )


def handle_work_assigned(envelope: dict) -> None:
    payload = envelope['payload']
    logger.info(
        'WorkAssigned work_id=%s assigned_to_id=%s previous=%s',
        payload.get('work_id'),
        payload.get('assigned_to_id'),
        payload.get('previous_assigned_to_id'),
    )


def handle_work_status_changed(envelope: dict) -> None:
    payload = envelope['payload']
    logger.info(
        'WorkStatusChanged work_id=%s status=%s previous=%s',
        payload.get('work_id'),
        payload.get('status'),
        payload.get('previous_status'),
    )


HANDLERS = {
    EventNames.WORK_CREATED: handle_work_created,
    EventNames.WORK_ASSIGNED: handle_work_assigned,
    EventNames.WORK_STATUS_CHANGED: handle_work_status_changed,
}
