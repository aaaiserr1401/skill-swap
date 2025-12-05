from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Skill, ExchangeRequest


User = get_user_model()


class SkillSlugTests(TestCase):
    def test_slug_generated_from_name(self):
        skill = Skill.objects.create(name="Python Basics")
        self.assertTrue(skill.slug)
        self.assertIn("python-basics", skill.slug)

    def test_slug_uniqueness_on_same_name(self):
        # name уникален, поэтому используем разные варианты,
        # которые после slugify дают одинаковую базу "python"
        first = Skill.objects.create(name="Python")
        second = Skill.objects.create(name="Python ")
        third = Skill.objects.create(name="PYTHON")

        self.assertEqual(first.slug, "python")
        self.assertNotEqual(second.slug, first.slug)
        self.assertNotEqual(third.slug, first.slug)
        self.assertNotEqual(third.slug, second.slug)


class ExchangeRequestModelTests(TestCase):
    def setUp(self) -> None:
        self.sender = User.objects.create_user(username="sender", password="pass", points=20)
        self.receiver = User.objects.create_user(username="receiver", password="pass", points=0)
        self.skill = Skill.objects.create(name="Python")

    def test_hold_from_sender_success(self):
        ex = ExchangeRequest(sender=self.sender, receiver=self.receiver, skill=self.skill, price=5)
        ok = ex.hold_from_sender()
        self.assertTrue(ok)
        self.sender.refresh_from_db()
        self.assertEqual(self.sender.points, 15)
        self.assertEqual(self.sender.points_hold, 5)

    def test_hold_from_sender_insufficient_points(self):
        self.sender.points = 3
        self.sender.save()
        ex = ExchangeRequest(sender=self.sender, receiver=self.receiver, skill=self.skill, price=5)
        ok = ex.hold_from_sender()
        self.assertFalse(ok)
        self.sender.refresh_from_db()
        self.assertEqual(self.sender.points, 3)
        self.assertEqual(self.sender.points_hold, 0)

    def test_refund_to_sender_returns_hold(self):
        ex = ExchangeRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            skill=self.skill,
            price=5,
            status=ExchangeRequest.STATUS_PENDING,
        )
        ex.hold_from_sender()
        self.sender.refresh_from_db()
        self.assertEqual(self.sender.points, 15)
        self.assertEqual(self.sender.points_hold, 5)

        ex.refund_to_sender()
        self.sender.refresh_from_db()
        ex.refresh_from_db()
        self.assertEqual(self.sender.points, 20)
        self.assertEqual(self.sender.points_hold, 0)
        self.assertEqual(ex.status, ExchangeRequest.STATUS_DECLINED)

    def test_try_complete_moves_points_and_sets_completed(self):
        ex = ExchangeRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            skill=self.skill,
            price=5,
            status=ExchangeRequest.STATUS_PENDING,
        )
        ex.hold_from_sender()

        ex.sender_confirmed = True
        ex.receiver_confirmed = True
        ex.status = ExchangeRequest.STATUS_ACCEPTED
        ex.save(update_fields=["sender_confirmed", "receiver_confirmed", "status"])

        completed = ex.try_complete()
        self.assertTrue(completed)

        self.sender.refresh_from_db()
        self.receiver.refresh_from_db()
        ex.refresh_from_db()

        # price 5: 20 старт - 5 hold = 15, затем try_complete: 15 - 5 + 10 = 20
        # у получателя 0 + 5 + 10 = 15 (с учётом текущей логики модели)
        self.assertEqual(self.sender.points, 20)
        self.assertEqual(self.sender.points_hold, 0)
        self.assertEqual(self.receiver.points, 15)
        self.assertEqual(ex.status, ExchangeRequest.STATUS_COMPLETED)


class ExchangeViewsTests(TestCase):
    def setUp(self) -> None:
        self.sender = User.objects.create_user(username="sender", password="pass", points=20)
        self.receiver = User.objects.create_user(username="receiver", password="pass", points=0)
        self.viewer = User.objects.create_user(username="viewer", password="pass", points=0)
        self.skill = Skill.objects.create(name="Python")

    def test_exchange_create_view_creates_request_and_holds_points(self):
        url = reverse("accounts:exchange_create")
        self.client.login(username="sender", password="pass")
        response = self.client.post(url, {"receiver": self.receiver.id, "skill": self.skill.id})
        self.assertEqual(response.status_code, 302)
        ex = ExchangeRequest.objects.get(sender=self.sender, receiver=self.receiver)
        self.sender.refresh_from_db()
        self.assertEqual(ex.skill, self.skill)
        self.assertEqual(self.sender.points, 15)
        self.assertEqual(self.sender.points_hold, 5)

    def test_send_request_view_uses_target_skill(self):
        # назначим навык как преподаваемый получателем
        self.receiver.skills_can_teach.add(self.skill)
        url = reverse("accounts:send_request", args=[self.receiver.id])
        self.client.login(username="sender", password="pass")
        response = self.client.post(url, {"skill": self.skill.id, "message": "hi"})
        self.assertEqual(response.status_code, 302)
        ex = ExchangeRequest.objects.get(sender=self.sender, receiver=self.receiver)
        self.assertEqual(ex.skill, self.skill)

    def test_user_search_filters_by_skill_and_mode(self):
        # sender может преподавать Python, receiver хочет изучать
        self.sender.skills_can_teach.add(self.skill)
        self.receiver.skills_to_learn.add(self.skill)

        url = reverse("accounts:user_search")

        # Заходим под третьим пользователем, чтобы sender/receiver
        # не отфильтровались как текущий пользователь
        self.client.login(username="viewer", password="pass")

        # ищем тех, кто может преподавать Python
        resp_teach = self.client.get(url, {"mode": "teach", "skill": "Python"})
        self.assertContains(resp_teach, "sender")
        self.assertNotContains(resp_teach, "receiver")

        # ищем тех, кто хочет изучить Python
        resp_learn = self.client.get(url, {"mode": "learn", "skill": "Python"})
        self.assertContains(resp_learn, "receiver")
        self.assertNotContains(resp_learn, "sender")

