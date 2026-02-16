from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Organization

User = get_user_model()

class OrganizationRegistrationTests(APITestCase):
    def test_register_organization_and_user(self):
        url = reverse('register_organization')
        data = {
            'username': 'testadmin',
            'email': 'admin@testorg.com',
            'password': 'strongpassword123',
            'organization_name': 'Test Corp',
            'phone_number': '1234567890'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Verify DB
        self.assertEqual(Organization.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().organization.name, 'Test Corp')

    def test_login_user(self):
        # Setup
        org = Organization.objects.create(name='Login Corp')
        user = User.objects.create_user(username='loginuser', password='password123', organization=org)
        
        url = reverse('token_obtain_pair')
        data = {
            'username': 'loginuser',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
