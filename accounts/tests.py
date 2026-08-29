from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AccountsApiTests(APITestCase):
    def test_register_and_me(self):
        response = self.client.post('/api/register/', {
            'organization_name': 'Test Agency',
            'username': 'admin',
            'email': 'admin@example.com',
            'phone_number': '+1 555 1000',
            'password': 'strong-test-password-123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['organization']['name'], 'Test Agency')

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        me = self.client.get('/api/me/')
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data['username'], 'admin')

    def test_me_requires_authentication(self):
        response = self.client.get(reverse('current_user'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
