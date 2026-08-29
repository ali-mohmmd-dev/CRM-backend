import json
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.utils import timezone

from accounts.models import Organization
from customers.models import Customer
from events.envelope import build_envelope
from events.handlers.leads import handle_lead_converted
from events.handlers.registry import dispatch, register_handlers
from events.producer import publish, reset_producer
from events.types import EventNames


class LeadConvertedHandlerTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name='Handler Org')

    def _envelope(self):
        return build_envelope(
            EventNames.LEAD_CONVERTED,
            self.organization.id,
            {
                'lead_id': 99,
                'organization_id': self.organization.id,
                'name': 'Robert Brown',
                'company': 'Beta Labs',
                'email': 'robert@example.com',
                'phone': '+1 555 0301',
                'notes': 'Hot lead',
                'last_contact': timezone.localdate().isoformat(),
            },
        )

    def test_lead_converted_creates_customer(self):
        handle_lead_converted(self._envelope())
        customer = Customer.objects.get(
            organization=self.organization,
            email='robert@example.com',
        )
        self.assertEqual(customer.name, 'Robert Brown')
        self.assertEqual(customer.status, Customer.STATUS_ACTIVE)

    def test_lead_converted_is_idempotent(self):
        handle_lead_converted(self._envelope())
        handle_lead_converted(self._envelope())
        self.assertEqual(
            Customer.objects.filter(
                organization=self.organization,
                email='robert@example.com',
            ).count(),
            1,
        )

    def test_dispatch_routes_lead_converted(self):
        register_handlers()
        dispatch(self._envelope())
        self.assertTrue(Customer.objects.filter(email='robert@example.com').exists())


@override_settings(
    KAFKA_BOOTSTRAP_SERVERS='localhost:9092',
    KAFKA_CLIENT_ID='crm-test',
    KAFKA_TOPICS={
        'leads': 'crm.lead.events',
        'customers': 'crm.customer.events',
        'works': 'crm.work.events',
    },
)
class ProducerTests(TestCase):
    def tearDown(self):
        reset_producer()

    @patch('events.producer.get_producer')
    def test_publish_sends_json_envelope(self, mock_get_producer):
        producer = MagicMock()
        mock_get_producer.return_value = producer

        envelope = publish(
            'leads',
            EventNames.LEAD_CALLED,
            organization_id=7,
            payload={
                'lead_id': 1,
                'organization_id': 7,
                'status': 'contacted',
                'called_at': '2026-08-29T00:00:00+00:00',
            },
            key='1',
        )

        producer.produce.assert_called_once()
        kwargs = producer.produce.call_args.kwargs
        self.assertEqual(kwargs['topic'], 'crm.lead.events')
        self.assertEqual(kwargs['key'], b'1')
        body = json.loads(kwargs['value'].decode('utf-8'))
        self.assertEqual(body['event_type'], EventNames.LEAD_CALLED)
        self.assertEqual(body['organization_id'], 7)
        self.assertEqual(body['payload']['lead_id'], 1)
        self.assertEqual(envelope['event_type'], EventNames.LEAD_CALLED)
        producer.flush.assert_called_once()
