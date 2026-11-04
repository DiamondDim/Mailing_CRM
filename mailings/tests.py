from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import Client, Message, Mailing, MailingAttempt, Profile
from .forms import ClientForm, MessageForm, MailingForm, RegisterForm

User = get_user_model()


# ==========================================
# ТЕСТЫ МОДЕЛЕЙ
# ==========================================
class ClientModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # ВАЖНО: называем client_obj, чтобы не перекрывать self.client (тестовый клиент Django)
        self.client_obj = Client.objects.create(
            email='test@test.com',
            full_name='Иванов Иван',
            comment='Тестовый клиент',
            owner=self.user
        )

    def test_client_creation(self):
        self.assertEqual(self.client_obj.email, 'test@test.com')
        self.assertEqual(self.client_obj.full_name, 'Иванов Иван')

    def test_client_owner(self):
        self.assertEqual(self.client_obj.owner, self.user)


class MessageModelTest(TestCase):
    def setUp(self):
        self.message = Message.objects.create(
            subject='Тестовая тема',
            body='Тестовое тело сообщения'
        )

    def test_message_creation(self):
        self.assertEqual(self.message.subject, 'Тестовая тема')
        self.assertEqual(self.message.body, 'Тестовое тело сообщения')


class MailingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.message = Message.objects.create(subject='Test', body='Test body')
        self.client_obj = Client.objects.create(
            email='test@test.com',
            full_name='Test Client',
            owner=self.user
        )
        self.mailing = Mailing.objects.create(
            message=self.message,
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(days=1),
            owner=self.user
        )
        self.mailing.recipients.add(self.client_obj)

    def test_mailing_creation(self):
        self.assertEqual(self.mailing.message.subject, 'Test')
        self.assertEqual(self.mailing.recipients.count(), 1)

    def test_mailing_update_status_created(self):
        self.mailing.start_time = timezone.now() + timedelta(hours=1)
        self.mailing.save()
        self.mailing.update_status()
        self.assertEqual(self.mailing.status, 'created')

    def test_mailing_update_status_started(self):
        self.mailing.update_status()
        self.assertEqual(self.mailing.status, 'started')

    def test_mailing_update_status_completed(self):
        self.mailing.end_time = timezone.now() - timedelta(hours=1)
        self.mailing.save()
        self.mailing.update_status()
        self.assertEqual(self.mailing.status, 'completed')


class MailingAttemptModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.message = Message.objects.create(subject='Test', body='Test')
        self.mailing = Mailing.objects.create(
            message=self.message,
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(days=1),
            owner=self.user
        )
        self.attempt = MailingAttempt.objects.create(
            mailing=self.mailing,
            status='success',
            server_response='OK'
        )

    def test_attempt_creation(self):
        self.assertEqual(self.attempt.status, 'success')
        self.assertEqual(self.attempt.server_response, 'OK')


# ==========================================
# ТЕСТЫ ФОРМ
# ==========================================
class ClientFormTest(TestCase):
    def test_client_form_valid(self):
        form = ClientForm(data={
            'email': 'test@test.com',
            'full_name': 'Иванов Иван',
            'comment': 'Комментарий'
        })
        self.assertTrue(form.is_valid())

    def test_client_form_invalid_email(self):
        form = ClientForm(data={
            'email': 'invalid-email',
            'full_name': 'Иванов Иван'
        })
        self.assertFalse(form.is_valid())


class MailingFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # ВАЖНО: создаем сообщение с владельцем!
        self.message = Message.objects.create(
            subject='Test',
            body='Test',
            owner=self.user
        )
        self.client_obj = Client.objects.create(
            email='test@test.com',
            full_name='Test',
            owner=self.user
        )

    def test_mailing_form_valid(self):
        # Используем дни вместо часов, чтобы избежать ловушки часовых поясов
        # (строка теряет таймзону, форма считает её московским временем, а timezone.now() — это UTC)
        start = timezone.now() + timedelta(days=1)
        end = timezone.now() + timedelta(days=2)

        form = MailingForm(data={
            'start_time': start.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end.strftime('%Y-%m-%dT%H:%M'),
            'message': self.message.id,
            'recipients': [self.client_obj.id]
        }, user=self.user) # <-- Передаем user для фильтрации полей message и recipients

        self.assertTrue(form.is_valid(), form.errors)

    def test_mailing_form_start_in_past(self):
        start = timezone.now() - timedelta(hours=2)
        end = timezone.now() + timedelta(days=2)
        form = MailingForm(data={
            'start_time': start.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end.strftime('%Y-%m-%dT%H:%M'),
            'message': self.message.id,
            'recipients': [self.client_obj.id]
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_mailing_form_start_after_end(self):
        start = timezone.now() + timedelta(days=2)
        end = timezone.now() + timedelta(days=1)
        form = MailingForm(data={
            'start_time': start.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end.strftime('%Y-%m-%dT%H:%M'),
            'message': self.message.id,
            'recipients': [self.client_obj.id]
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)


class RegisterFormTest(TestCase):
    def test_register_form_valid(self):
        form = RegisterForm(data={
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertTrue(form.is_valid())


# ==========================================
# ТЕСТЫ VIEW (ИНТЕГРАЦИОННЫЕ)
# ==========================================
class HomeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_home_view_status_code(self):
        """Тест доступности главной страницы"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_uses_correct_template(self):
        """Тест содержимого главной страницы (вместо assertTemplateUsed из-за cache_page)"""
        response = self.client.get(reverse('home'))
        # Проверяем наличие характерного текста из шаблона home.html
        self.assertContains(response, 'Панель управления рассылками')


class ClientListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client_obj = Client.objects.create(
            email='test@test.com',
            full_name='Test Client',
            owner=self.user
        )

    def test_client_list_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('client_list'))
        self.assertEqual(response.status_code, 302)

    def test_client_list_logged_in(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Client')


class RegisterViewTest(TestCase):
    def setUp(self):
        pass  # self.client уже доступен из TestCase

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mailings/register.html')

    def test_register_view_post_creates_inactive_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        user = User.objects.get(username='newuser')
        self.assertFalse(user.is_active)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_profile_view_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_logged_in(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')


# ==========================================
# ТЕСТЫ МИКСИНОВ
# ==========================================
class OwnerRequiredMixinTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.client_obj = Client.objects.create(
            email='test@test.com',
            full_name='Test',
            owner=self.user1
        )

    def test_owner_can_update_own_client(self):
        self.client.login(username='user1', password='pass1')
        response = self.client.get(reverse('client_update', args=[self.client_obj.id]))
        self.assertEqual(response.status_code, 200)

    def test_non_owner_cannot_update_other_client(self):
        self.client.login(username='user2', password='pass2')
        response = self.client.get(reverse('client_update', args=[self.client_obj.id]))
        self.assertEqual(response.status_code, 403)  # Permission Denied


class MailingPermissionTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.message = Message.objects.create(
            subject='Test',
            body='Test',
            owner=self.user1
        )
        self.client_obj = Client.objects.create(
            email='t@t.com',
            full_name='Test',
            owner=self.user1
        )
        self.mailing = Mailing.objects.create(
            message=self.message,
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(days=1),
            owner=self.user1
        )

    def test_non_owner_cannot_view_mailing_detail(self):
        """Тест: пользователь 2 не может открыть детальную страницу рассылки пользователя 1"""
        self.client.login(username='user2', password='pass2')
        response = self.client.get(reverse('mailing_detail', args=[self.mailing.id]))
        self.assertEqual(response.status_code, 404)  # get_queryset отфильтрует и вернет 404

    def test_non_owner_cannot_update_other_mailing(self):
        """Тест: пользователь 2 не может изменить рассылку пользователя 1 (проверка OwnerRequiredMixin)"""
        self.client.login(username='user2', password='pass2')
        response = self.client.get(reverse('mailing_update', args=[self.mailing.id]))
        self.assertEqual(response.status_code, 403)  # Permission Denied

def test_non_owner_cannot_send_other_mailing(self):
    self.client.login(username="user2", password="pass2")

    response = self.client.post(
        reverse("mailing_send", args=[self.mailing.id])
    )

    self.assertEqual(response.status_code, 404)
    self.assertFalse(
        MailingAttempt.objects.filter(mailing=self.mailing).exists()
    )
