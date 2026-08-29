import json
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.events.envelope import build_envelope
from core.events.handlers.leads import handle_lead_converted
from core.events.handlers.registry import dispatch, register_handlers
from core.events.producer import publish, reset_producer
from core.events.types import EventNames
from core.models import Customer, Organization


class CRMApiTests(APITestCase):
    def register_and_authenticate(self):
        response = self.client.post('/api/register/', {
            'organization_name': 'Test Agency',
            'username': 'admin',
            'email': 'admin@example.com',
            'phone_number': '+1 555 1000',
            'password': 'strong-test-password-123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response.data

    @patch('core.views.publish')
    def test_crm_end_to_end_flow(self, mock_publish):
        auth_payload = self.register_and_authenticate()
        self.assertEqual(auth_payload['user']['organization']['name'], 'Test Agency')

        staff_response = self.client.post('/api/staff/', {
            'name': 'Sarah Johnson',
            'email': 'sarah@example.com',
            'role': 'Account Manager',
            'phone': '+1 555 0101',
        }, format='json')
        self.assertEqual(staff_response.status_code, status.HTTP_201_CREATED)
        staff_id = staff_response.data['id']

        work_response = self.client.post('/api/works/', {
            'title': 'Launch campaign',
            'description': 'Prepare paid media launch',
            'assignedTo': staff_id,
            'status': 'pending',
            'priority': 'high',
            'dueDate': '2026-06-01',
        }, format='json')
        self.assertEqual(work_response.status_code, status.HTTP_201_CREATED)

        customer_response = self.client.post('/api/customers/', {
            'name': 'John Smith',
            'company': 'Acme Corp',
            'email': 'john@example.com',
            'phone': '+1 555 0201',
            'status': 'prospect',
            'lastContact': '2026-05-22',
            'notes': 'Interested in branding',
        }, format='json')
        self.assertEqual(customer_response.status_code, status.HTTP_201_CREATED)
        customer_id = customer_response.data['id']

        follow_up_response = self.client.post(f'/api/customers/{customer_id}/follow-up/')
        self.assertEqual(follow_up_response.status_code, status.HTTP_200_OK)

        lead_response = self.client.post('/api/leads/', {
            'name': 'Robert Brown',
            'company': 'Beta Labs',
            'email': 'robert@example.com',
            'phone': '+1 555 0301',
            'source': 'Website',
            'status': 'new',
            'called': False,
            'notes': '',
            'value': 15000,
        }, format='json')
        self.assertEqual(lead_response.status_code, status.HTTP_201_CREATED)
        lead_id = lead_response.data['id']

        called_response = self.client.post(f'/api/leads/{lead_id}/mark-called/')
        self.assertEqual(called_response.status_code, status.HTTP_200_OK)
        self.assertTrue(called_response.data['called'])
        self.assertEqual(called_response.data['status'], 'contacted')

        dashboard_response = self.client.get('/api/dashboard/stats/')
        self.assertEqual(dashboard_response.status_code, status.HTTP_200_OK)
        self.assertEqual(dashboard_response.data['totalStaff'], 1)
        self.assertEqual(dashboard_response.data['totalWorks'], 1)
        self.assertEqual(dashboard_response.data['totalCustomers'], 1)
        self.assertEqual(dashboard_response.data['totalLeads'], 1)

        calendar_response = self.client.get('/api/calendar/?date=2026-06-01')
        self.assertEqual(calendar_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(calendar_response.data['works']), 1)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse('current_user'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('core.views.publish')
    def test_convert_to_customer_returns_202_and_publishes_event(self, mock_publish):
        self.register_and_authenticate()
        lead_response = self.client.post('/api/leads/', {
            'name': 'Robert Brown',
            'company': 'Beta Labs',
            'email': 'robert@example.com',
            'phone': '+1 555 0301',
            'source': 'Website',
            'status': 'new',
            'called': False,
            'notes': 'Hot lead',
            'value': 15000,
        }, format='json')
        lead_id = lead_response.data['id']

        with self.captureOnCommitCallbacks(execute=True):
            convert_response = self.client.post(f'/api/leads/{lead_id}/convert-to-customer/')

        self.assertEqual(convert_response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(convert_response.data['status'], 'converted')
        self.assertEqual(convert_response.data['id'], lead_id)

        mock_publish.assert_called()
        args, kwargs = mock_publish.call_args
        self.assertEqual(args[0], 'leads')
        self.assertEqual(args[1], EventNames.LEAD_CONVERTED)
        self.assertEqual(args[3]['email'], 'robert@example.com')
        self.assertEqual(Customer.objects.filter(email='robert@example.com').count(), 0)


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
        self.assertTrue(
            Customer.objects.filter(email='robert@example.com').exists()
        )


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

    @patch('core.events.producer.get_producer')
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
