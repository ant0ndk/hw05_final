import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from posts.models import Group, Post, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUp(self):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='AntonKarpov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тест',
            slug='7897987',
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group
        )
        self.form_data = {
            'text': 'formtesttext',
            'group': self.group.id,
        }
        self.new_post = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        # Templates
        self.public_index_template = 'posts/index.html'
        self.public_group_page_template = 'posts/group_list.html'
        self.private_create_post_template = 'posts/create_post.html'
        self.private_edit_post_template = 'posts/create_post.html'
        self.public_profile = 'posts/profile.html'
        self.public_post = 'posts/post_detail.html'
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    # Проверяем используемые шаблоны
    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: name"
        templates_pages_names = {
            self.public_index_template: reverse('posts:index'),
            self.public_profile: reverse('posts:profile',
                                         kwargs={'username': 'AntonKarpov'}),
            self.public_post: reverse('posts:post_detail',
                                      kwargs={'post_id': '1'}),
            self.private_edit_post_template: reverse('posts:post_edit',
                                                     kwargs={'post_id':
                                                             '1'}),
            self.private_create_post_template: reverse('posts:post_create'),
            self.public_group_page_template: (
                reverse('posts:group_list', kwargs={'slug': '7897987'})
            ),
        }
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, self.private_create_post_template)

    def test_context(self):
        url_names = [reverse('posts:index'),
                     reverse('posts:post_detail', kwargs={'post_id': '2'}),
                     reverse('posts:post_edit',
                             kwargs={'post_id': '2'}),
                     reverse('posts:group_list',
                             kwargs={'slug': self.group.slug}),
                     reverse('posts:profile',
                             kwargs={'username': self.user.username})]
        for url in url_names:
            response = self.authorized_client.get(url)
            self.assertContains(response, self.form_data['text'])
            self.assertContains(response, self.user)
            self.assertContains(response, self.group.id)

    def test_group_context(self):
        """Пост попадает в корректную группу."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args={self.group.slug})
        )
        post = response.context['posts'][1]
        self.assertEqual(post.pk, self.post.pk)

    def test_check_post_in_group(self):
        """Проверить пост в группе"""
        t_group = Group.objects.create(
            title='Заголовок',
            slug='test',
            description='Текст',
        )
        Group.objects.create(
            title='Заголовок1',
            slug='test1',
            description='Текст1',
        )
        Post.objects.create(
            text='formtesttext',
            author=self.user,
            group=t_group
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test'}))
        self.assertEqual(response.context['group'].title, 'Заголовок')
        self.assertEqual(response.context['group'].slug, 'test')
        self.assertEqual(response.context['group'].description, 'Текст')
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_group = first_object.group
        self.assertEqual(post_text, 'formtesttext')
        self.assertEqual(post_group.title, 'Заголовок')
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test1'})
        )
        self.assertFalse(response.context['page_obj'].has_next())

    def test_check_post_in_index(self):
        """Проверить пост в на главной странице"""
        response = self.authorized_client.get(
            reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        self.assertEqual(post_text, 'formtesttext')
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        self.assertFalse(response.context['page_obj'].has_next())

    def test_image_context(self):
        """Шаблон получает посты с изображениями."""
        urls = [
            reverse('posts:index'),
            reverse('posts:profile', args={self.user.username}),
            reverse('posts:group_list', args={self.group.slug}),
        ]
        for reverse_name in urls:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['posts'][0]
                post_image_0 = first_object.image
                self.assertEqual(post_image_0, self.post.image)
        response = self.authorized_client.get(
            reverse('posts:post_detail', args={self.post.pk})
        )
        post = response.context['post']
        self.assertEqual(post.image, self.post.image)


class PaginatorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='AntonKarpov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        for i in range(0, 13):
            Post.objects.create(
                text='Тестовый текст',
                author=self.user,)
        cache.clear()

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_author')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        cache.clear()

    def test_cache_index_page(self):
        """Запись остаётся на странице до принудительной очистки кэша"""
        response = self.authorized_author.get(reverse('posts:index'))
        content = response.content
        Post.objects.create(
            text='Тестовый пост',
            author=self.author,
        )
        response = self.authorized_author.get(reverse('posts:index'))
        self.assertEqual(content, response.content)
        cache.clear()
        response = self.authorized_author.get(reverse('posts:index'))
        self.assertNotEqual(content, response.content)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.author = User.objects.create_user(username='test_author')
        cls.follower = User.objects.create_user(username='test_follower')
        cls.post = Post.objects.create(
            text="Тестовый пост",
            author=cls.author
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)

    def test_follow(self):
        """Авторизованный пользователь может подписываться на авторов."""
        self.authorized_follower.get(
            reverse(
                'posts:profile_follow',
                args={self.author.username}
            )
        )
        follow_count = Follow.objects.filter(
            user=self.follower.id,
            author=self.author.id
        ).count()
        self.assertEqual(follow_count, 1)

    def test_unfollow(self):
        """Авторизованный пользователь может отписываться от авторов."""
        Follow.objects.create(user=self.follower, author=self.author)
        self.authorized_follower.get(
            reverse(
                'posts:profile_unfollow',
                args={self.author.username}
            )
        )
        follow_count = Follow.objects.filter(
            user=self.follower.id,
            author=self.author.id
        ).count()
        self.assertEqual(follow_count, 0)

    def test_post_in_follower_index(self):
        """Новая запись автора появляется в ленте подписчиков."""
        Follow.objects.create(user=self.follower, author=self.author)
        response = self.authorized_follower.get(reverse('posts:follow_index'))
        post = response.context['posts'][0]
        self.assertEqual(post.text, self.post.text)

    def test_post_not_in_user_index(self):
        """Новой записи автора нет в ленте неподписанных пользователей."""
        response = self.authorized_user.get(reverse('posts:follow_index'))
        posts = response.context['posts']
        self.assertNotIn(self.post, posts)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.author = User.objects.create_user(username='test_author')
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.author,
        )

    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
    
    def test_auth_can_create_comment(self):
        """Aвторизированный пользователь создаёт комментарий."""
        post = self.post
        comments_count = post.comments.count()
        form_data = {
            'text': 'Комментарий гостя',
        }
        response = self.authorized_author.post(
            reverse('posts:add_comment', args={self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args={self.post.pk}
            )
        )
        self.assertFalse(
            Post.objects.filter(text=form_data['text'],).exists()
        )
