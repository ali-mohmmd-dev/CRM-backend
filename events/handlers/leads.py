import logging

from django.utils import timezone
from django.utils.dateparse import parse_date

from customers.models import Customer

from ..types import EventNames

logger = logging.getLogger(__name__)


def handle_lead_called(envelope: dict) -> None:
    payload = envelope['payload']
    logger.info(
        'LeadCalled lead_id=%s organization_id=%s status=%s',
        payload.get('lead_id'),
        envelope.get('organization_id'),
        payload.get('status'),
    )


def handle_lead_converted(envelope: dict) -> None:
    payload = envelope['payload']
    organization_id = payload['organization_id']
    email = payload['email']
    last_contact = parse_date(payload['last_contact']) if payload.get('last_contact') else timezone.localdate()

    customer, created = Customer.objects.get_or_create(
        organization_id=organization_id,
        email=email,
        defaults={
            'name': payload['name'],
            'company': payload['company'],
            'phone': payload['phone'],
            'status': Customer.STATUS_ACTIVE,
            'last_contact': last_contact,
            'notes': payload.get('notes') or '',
        },
    )
    logger.info(
        'LeadConverted lead_id=%s customer_id=%s created=%s',
        payload.get('lead_id'),
        customer.id,
        created,
    )


HANDLERS = {
    EventNames.LEAD_CALLED: handle_lead_called,
    EventNames.LEAD_CONVERTED: handle_lead_converted,
}
