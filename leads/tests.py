from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import Customer
from events.types import EventNames


class LeadsApiTests(APITestCase):
    def register_and_authenticate(self):
        response = self.client.post('/api/register/', {
            'organization_name': 'Lead Org',
            'username': 'leadadmin',
            'email': 'leadadmin@example.com',
            'phone_number': '+1 555 1000',
            'password': 'strong-test-password-123',
        }, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response.data

    @patch('common.views.publish')
    def test_crm_end_to_end_flow(self, mock_publish):
        self.register_and_authenticate()

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

    @patch('common.views.publish')
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
