import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user1 = User.objects.create_user(username='NoName1')
        cls.authorized_client1 = Client()
        cls.authorized_client1.force_login(cls.user1)

        cls.group1 = Group.objects.create(
            title='Тестовая группа1',
            slug='test-slug1',
            description='Тестовое описание1',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        # картинка для теста
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post1 = Post.objects.create(
            author=cls.user1,
            text='Тестовый текст1',
            group=cls.group1,
            image=uploaded,
        )

    def test_pages_uses_correct_template(self):
        """VIEW-функции используют соответствующие шаблоны."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug1'}): 'posts/group_list.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post1.id}
                    ): 'posts/post_detail.html',
            reverse('posts:profile',
                    kwargs={'username': 'NoName1'}): 'posts/profile.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post1.id}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client1.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        post_object = response.context['page_obj'][0]
        author_0 = post_object.author
        text_0 = post_object.text
        group_0 = post_object.group
        image_0 = post_object.image
        self.assertEqual(author_0, self.user1)
        self.assertEqual(text_0, self.post1.text)
        self.assertEqual(group_0, self.post1.group)
        self.assertEqual(image_0, self.post1.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client1.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug1'}))
        self.assertIn('page_obj', response.context)
        post_object = response.context['page_obj'][0]
        author_0 = post_object.author
        text_0 = post_object.text
        group_0 = post_object.group
        image_0 = post_object.image
        self.assertEqual(author_0, self.user1)
        self.assertEqual(text_0, self.post1.text)
        self.assertEqual(group_0, self.post1.group)
        self.assertEqual(image_0, self.post1.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон Profile сформирован с правильным контекстом."""
        response = self.authorized_client1.get(
            reverse('posts:profile', kwargs={'username': 'NoName1'}))
        self.assertIn('page_obj', response.context)
        post_object = response.context['page_obj'][0]
        author_0 = post_object.author
        text_0 = post_object.text
        group_0 = post_object.group
        image_0 = post_object.image
        self.assertEqual(author_0, self.user1)
        self.assertEqual(text_0, self.post1.text)
        self.assertEqual(group_0, self.post1.group)
        self.assertEqual(image_0, self.post1.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client1.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        self.assertIn('post', response.context)
        post_object = response.context['post']
        author_0 = post_object.author
        text_0 = post_object.text
        group_0 = post_object.group
        image_0 = post_object.image
        self.assertEqual(author_0, self.user1)
        self.assertEqual(text_0, self.post1.text)
        self.assertEqual(group_0, self.post1.group)
        self.assertEqual(image_0, self.post1.image)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client1.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client1.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client1.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug1'}))
        self.assertIn('page_obj', response.context)
        post_object = response.context['page_obj'][0]
        post_group_0 = post_object.group
        self.assertNotEqual(post_group_0, self.group2)

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.authorized_client1.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            author=self.user1,
            text='Тестовый текст кэш2',
            group=self.group1,
        )
        response_old = self.authorized_client1.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client1.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)

    def test_follow_unfollow_usage(self):
        """Проверка пдописки и отписки от авторов."""
        self.user2 = User.objects.create_user(username='NoName2')
        self.post2 = Post.objects.create(
            author=self.user2,
            text='Тестовый текст2',
            group=self.group2,
        )
        self.authorized_client1.get(reverse('posts:profile_follow',
                                            kwargs={'username': 'NoName2'}))
        follow_response = self.authorized_client1.get(reverse
                                                      ('posts:follow_index'))
        page_obj = follow_response.context['page_obj'][0]
        text_0 = page_obj.text
        self.assertEqual(text_0, self.post2.text)
        self.authorized_client1.get(reverse('posts:profile_unfollow',
                                            kwargs={'username': 'NoName2'}))
        unfollow_response = self.authorized_client1.get(reverse
                                                        ('posts:follow_index'))
        self.assertNotEqual(follow_response, unfollow_response)

    def test_follow_displayed_correctly(self):
        self.user2 = User.objects.create_user(username='NoName2')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        self.post2 = Post.objects.create(
            author=self.user2,
            text='Тестовый текст2',
            group=self.group2,
        )
        self.authorized_client1.get(reverse('posts:profile_follow',
                                            kwargs={'username': 'NoName2'}))
        follow_response = self.authorized_client1.get(reverse
                                                      ('posts:follow_index'))
        page_obj = follow_response.context['page_obj'][0]
        text_0 = page_obj.text
        self.assertEqual(text_0, self.post2.text)
        nofollow_response = self.authorized_client2.get(reverse
                                                        ('posts:follow_index'))
        self.assertNotContains(nofollow_response, self.post1.text)


class PostsViewsPaginatorTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user3 = User.objects.create_user(username='NoName3')
        cls.authorized_client3 = Client()
        cls.authorized_client3.force_login(cls.user3)

        cls.post: list = []
        posts_number = 13
        for post in range(posts_number):
            cls.post.append(Post(text=f'Тестовый пост {posts_number}',
                                 author=cls.user3))
        Post.objects.bulk_create(cls.post)

    def test_first_page_contains_ten_records(self):
        """Количество постов на первой странице равно 10."""
        cache.clear()
        response = self.authorized_client3.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Количество постов на второй странице равно 3."""
        response = self.authorized_client3.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(Post.objects.count(), 13)
        self.assertEqual(len(response.context['page_obj']), 3)
