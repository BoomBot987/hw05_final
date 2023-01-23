from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем неавторизованный клиент
        cls.guest_client = Client()
        # Создаем пользователя 1
        cls.user1 = User.objects.create_user(username='NoName1')
        # Создаем второй клиент
        cls.authorized_client1 = Client()
        # Авторизуем пользователя
        cls.authorized_client1.force_login(cls.user1)

    def test_signup_url_exists_at_desired_location(self):
        """Страница /auth/signup/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_url_exists_at_desired_location(self):
        """Страница /auth/login/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/login/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_url_exists_at_desired_location(self):
        """Страница /auth/logout/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/',
            'users/logged_out.html': '/auth/logout/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client1.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template(self):
        """VIEW-функция используют соответствующий шаблон."""
        response = self.guest_client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')
