import logging

from ..types import EventNames

logger = logging.getLogger(__name__)


def handle_customer_followed_up(envelope: dict) -> None:
    payload = envelope['payload']
    logger.info(
        'CustomerFollowedUp customer_id=%s organization_id=%s last_contact=%s',
        payload.get('customer_id'),
        envelope.get('organization_id'),
        payload.get('last_contact'),
    )


HANDLERS = {
    EventNames.CUSTOMER_FOLLOWED_UP: handle_customer_followed_up,
}
