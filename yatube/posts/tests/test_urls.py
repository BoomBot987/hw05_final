from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user1 = User.objects.create_user(username='NoName1')
        cls.authorized_client1 = Client()
        cls.authorized_client1.force_login(cls.user1)
        cls.user2 = User.objects.create_user(username='NoName2')
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)

        Post.objects.create(
            text='Тестовый текст',
            author=cls.user1,
        )
        Group.objects.create(
            title='Тестовая группа',
            slug='test-slug1',
            description='Тестовое описание',
        )

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/<slug>/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug1/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_detail_url_exists_at_desired_location(self):
        """Страница /posts/<id>/ доступна любому пользователю."""
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/NoName1/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_detail_edit_url_exists_at_desired_location(self):
        """Страница /posts/<id>/edit/ доступна автору поста."""
        response = self.authorized_client1.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_create_url_exists_at_desired_location(self):
        """Страница /posts/create/
        доступна только авторизованному пользователю.
        """
        response = self.authorized_client2.get('/posts/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_detail_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /posts/<id>/edit/ перенаправит пользователя
        не являющегося автором поста на страницу /posts/<id>/.
        """
        response = self.authorized_client2.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_posts_create_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /posts/create/ перенаправит
        неавторизованного пользователя на страницу /auth/login/.
        """
        response = self.guest_client.get('/posts/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/create/')

    def test_urls_uses_correct_template(self):
        """URL-адрес используют соответствующие шаблоны."""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug1/': 'posts/group_list.html',
            '/posts/1/': 'posts/post_detail.html',
            '/profile/NoName1/': 'posts/profile.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/posts/create/': 'posts/create_post.html',

        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client1.get(address)
                self.assertTemplateUsed(response, template)
