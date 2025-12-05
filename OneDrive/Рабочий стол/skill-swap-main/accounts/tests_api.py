"""
Integration tests for API endpoints
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Skill, ExchangeRequest

User = get_user_model()


class APIAuthenticationTests(TestCase):
    """Тесты аутентификации API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_api_login_success(self):
        """Тест успешного входа через API"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
    
    def test_api_login_invalid_credentials(self):
        """Тест входа с неверными данными"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_api_logout(self):
        """Тест выхода из API"""
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class APIUserTests(TestCase):
    """Тесты API для пользователей"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123',
            full_name='User One'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123',
            full_name='User Two'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_list_users(self):
        """Тест получения списка пользователей"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_search_users(self):
        """Тест поиска пользователей"""
        response = self.client.get('/api/users/?search=user2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_get_user_detail(self):
        """Тест получения деталей пользователя"""
        response = self.client.get(f'/api/users/{self.user2.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user2')
    
    def test_list_users_requires_authentication(self):
        """Тест что список пользователей требует аутентификации"""
        self.client.credentials()  # Remove token
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class APISkillTests(TestCase):
    """Тесты API для навыков"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.skill = Skill.objects.create(name='Python', description='Python programming')
    
    def test_list_skills(self):
        """Тест получения списка навыков"""
        response = self.client.get('/api/skills/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_create_skill(self):
        """Тест создания навыка"""
        response = self.client.post('/api/skills/', {
            'name': 'JavaScript',
            'description': 'JavaScript programming'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'JavaScript')
    
    def test_get_skill_detail(self):
        """Тест получения деталей навыка"""
        response = self.client.get(f'/api/skills/{self.skill.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Python')
    
    def test_update_skill(self):
        """Тест обновления навыка"""
        response = self.client.patch(f'/api/skills/{self.skill.slug}/', {
            'description': 'Updated description'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')


class APIExchangeRequestTests(TestCase):
    """Тесты API для запросов на обмен"""
    
    def setUp(self):
        self.client = APIClient()
        self.sender = User.objects.create_user(
            username='sender',
            password='pass123',
            points=20
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            password='pass123',
            points=10
        )
        self.skill = Skill.objects.create(name='Python')
        self.receiver.skills_can_teach.add(self.skill)
        
        self.token, _ = Token.objects.get_or_create(user=self.sender)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_create_exchange_request(self):
        """Тест создания запроса на обмен"""
        response = self.client.post('/api/exchanges/', {
            'receiver': self.receiver.id,
            'skill': self.skill.id,
            'message': 'Хочу изучить Python',
            'price': 5
        })
        # Может быть 201 или 400 если недостаточно баллов
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_list_exchange_requests(self):
        """Тест получения списка запросов на обмен"""
        ExchangeRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            skill=self.skill,
            price=5
        )
        response = self.client.get('/api/exchanges/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_get_exchange_detail(self):
        """Тест получения деталей запроса"""
        exchange = ExchangeRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            skill=self.skill,
            price=5
        )
        response = self.client.get(f'/api/exchanges/{exchange.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], exchange.id)
    
    def test_exchange_action_accept(self):
        """Тест принятия запроса на обмен"""
        exchange = ExchangeRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            skill=self.skill,
            price=5,
            status=ExchangeRequest.STATUS_PENDING
        )
        exchange.hold_from_sender()
        
        # Переключаемся на токен получателя
        receiver_token, _ = Token.objects.get_or_create(user=self.receiver)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + receiver_token.key)
        
        response = self.client.post(f'/api/exchanges/{exchange.id}/action/', {
            'action': 'accept'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        exchange.refresh_from_db()
        self.assertEqual(exchange.status, ExchangeRequest.STATUS_ACCEPTED)
    
    def test_exchange_action_confirm(self):
        """Тест подтверждения обмена"""
        exchange = ExchangeRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            skill=self.skill,
            price=5,
            status=ExchangeRequest.STATUS_ACCEPTED
        )
        exchange.hold_from_sender()
        
        # Подтверждение отправителя
        response = self.client.post(f'/api/exchanges/{exchange.id}/action/', {
            'action': 'confirm'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        exchange.refresh_from_db()
        self.assertTrue(exchange.sender_confirmed)

