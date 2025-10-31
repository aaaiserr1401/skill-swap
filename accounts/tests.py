from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()


class AuthViewsTests(TestCase):
    def test_register_login_flow(self):
        # Register
        resp = self.client.post(reverse('accounts:register'), {
            'username': 'alice',
            'email': 'alice@example.com',
            'password1': 'StrongPass12345',
            'password2': 'StrongPass12345',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username='alice').exists())

        # Login
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'alice', 'password': 'StrongPass12345'
        })
        self.assertEqual(resp.status_code, 302)


class ApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='Secret12345')
        self.client_api = APIClient()

    def test_users_list_requires_auth(self):
        url = reverse('api:user-list')
        resp = self.client_api.get(url)
        self.assertIn(resp.status_code, (401, 403))

    def test_users_list_ok_with_auth(self):
        self.client_api.force_authenticate(user=self.user)
        url = reverse('api:user-list')
        resp = self.client_api.get(url)
        self.assertEqual(resp.status_code, 200)

# Create your tests here.
