from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from .models import Skill, ExchangeRequest


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
        self.other = User.objects.create_user(username='kate', password='Secret12345')
        self.skill = Skill.objects.create(name='Python')
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

    def test_create_exchange_holds_points(self):
        self.user.points = 20
        self.user.points_hold = 0
        self.user.save(update_fields=['points', 'points_hold'])
        self.client_api.force_authenticate(user=self.user)
        url = reverse('api:exchange-list')
        resp = self.client_api.post(url, {
            'receiver': self.other.id,
            'skill': self.skill.id,
            'message': 'Help me',
            'price': 5,
        })
        self.assertEqual(resp.status_code, 201)
        self.user.refresh_from_db()
        self.assertEqual(self.user.points, 15)
        self.assertEqual(self.user.points_hold, 5)

    def test_decline_refunds_hold(self):
        # Prepare exchange
        ex = ExchangeRequest.objects.create(
            sender=self.user,
            receiver=self.other,
            skill=self.skill,
            price=5,
            status=ExchangeRequest.STATUS_PENDING,
        )
        # Put 5 on hold
        self.user.points = 15
        self.user.points_hold = 5
        self.user.save(update_fields=['points', 'points_hold'])
        self.client_api.force_authenticate(user=self.other)
        url = reverse('api:exchange-action', args=[ex.id])
        resp = self.client_api.post(url, { 'action': 'decline' })
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        ex.refresh_from_db()
        self.assertEqual(self.user.points, 20)
        self.assertEqual(self.user.points_hold, 0)
        self.assertEqual(ex.status, ExchangeRequest.STATUS_DECLINED)

    def test_complete_awards_points(self):
        # Exchange accepted and both confirm
        ex = ExchangeRequest.objects.create(
            sender=self.user,
            receiver=self.other,
            skill=self.skill,
            price=5,
            status=ExchangeRequest.STATUS_ACCEPTED,
        )
        self.client_api.force_authenticate(user=self.user)
        url = reverse('api:exchange-action', args=[ex.id])
        self.client_api.post(url, { 'action': 'confirm' })
        self.client_api.force_authenticate(user=self.other)
        resp = self.client_api.post(url, { 'action': 'confirm' })
        self.assertEqual(resp.status_code, 200)
        ex.refresh_from_db()
        self.user.refresh_from_db()
        self.other.refresh_from_db()
        self.assertEqual(ex.status, ExchangeRequest.STATUS_COMPLETED)

# Create your tests here.
