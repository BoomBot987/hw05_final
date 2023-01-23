from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Group, Post, Comment

User = get_user_model()


class PostsCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user1 = User.objects.create_user(username='NoName1')
        cls.authorized_client1 = Client()
        cls.authorized_client1.force_login(cls.user1)

        cls.group1 = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug1',
            description='Тестовое описание',
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

    def test_create_post(self):
        """Проверка создания поста."""
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
        form_data = {
            'text': 'Тестовый текст созданного поста1',
            'group': self.group1.id,
            'image': uploaded,
        }
        posts_count = Post.objects.count()
        self.authorized_client1.post(reverse('posts:post_create'),
                                     data=form_data,
                                     follow=True)
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Проверка изменения поста."""
        form_data = {
            'text': 'Измененный текст тест1',
            'group': self.group1.id,
        }
        self.authorized_client1.post(reverse('posts:post_edit',
                                             kwargs={'post_id': self.post1.id}
                                             ),
                                     data=form_data,
                                     follow=True)
        self.assertTrue(Post.objects.filter(
            id=self.post1.id,
            text='Измененный текст тест1',
            group=self.group1.id,
            author=self.user1,
        ).exists())
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.text, form_data['text'])

    def test_create_comment(self):
        """Проверка создания комментария
        только авторизованным позльзователем.
        """
        form_data = {
            'text': 'Тестовый коментарий1',
        }
        comments_count = Comment.objects.count()
        self.guest_client.post(reverse('posts:add_comment',
                                       kwargs={'post_id': self.post1.id}),
                               data=form_data,
                               follow=True)
        self.assertNotEqual(Comment.objects.count(), comments_count + 1)
        self.authorized_client1.post(reverse('posts:add_comment',
                                             kwargs={'post_id': self.post1.id}
                                             ),
                                     data=form_data,
                                     follow=True)
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_display_comment(self):
        """Проверка создания комментария
        отображается на странице поста.
        """
        form_data = {
            'text': 'Тестовый коментарий1',
        }
        self.authorized_client1.post(reverse('posts:add_comment',
                                             kwargs={'post_id': self.post1.id}
                                             ),
                                     data=form_data,
                                     follow=True)
        self.post1.refresh_from_db()
        response = self.authorized_client1.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        self.assertIn('comments', response.context)
        comment_object = response.context['comments'][0]
        comment_0 = comment_object.text
        self.assertEqual(comment_0, form_data['text'])
