from posts.models import Group, Post
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus
from django.core.cache import cache

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user1 = User.objects.create_user(username='noauthor')
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)
        self.group = Group.objects.create(title='Тестовое сообщество',
                                          slug='testslug')
        self.post = Post.objects.create(
            text="Тестовый текст",
            author=self.user)
        # URLs
        self.public_index_url = '/'
        self.unexisting_page = '/unexisting_page/'
        self.public_group_page_url = '/group/testslug/'
        self.private_create_post_url = '/create/'  # авторизованный
        self.public_create_post_url = '/auth/login/?next=/create/'
        self.public_test_username = '/profile/author/'
        self.public_test_id_post = '/posts/1/'
        self.private_test_username_post_edit = '/posts/1/edit/'  # только автор
        self.templates_url_names = {
            '/': 'posts/index.html',
            '/group/testslug/': 'posts/group_list.html',
            '/posts/1/edit/':
                'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/': 'posts/post_detail.html',
            '/profile/author/': 'posts/profile.html'
        }
        self.url_list_for_guest = [self.public_index_url,
                                   self.public_group_page_url,
                                   self.public_test_username,
                                   self.public_test_id_post]
        self.url_list_for_auth = [
            self.private_create_post_url,
            self.private_test_username_post_edit
        ]
        cache.clear()

    def test_URls_for_guest(self):
        """Страницы доступные любому пользователю."""
        for url in self.url_list_for_guest:
            with self.subTest(url=url):
                response = self.guest_client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_URls_for_auth(self):
        """Страницы доступные любому пользователю."""
        for url in self.url_list_for_auth:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        response = self.guest_client.get(self.unexisting_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_new_post_unauth_user_redirect_login(self):
        response = self.guest_client.get(self.private_create_post_url,
                                         follow=True)
        self.assertRedirects(response, self.public_create_post_url)

    def test_post_edit_no_auth(self):
        response = self.guest_client.get(
            (self.private_test_username_post_edit),
            follow=True
        )
        self.assertRedirects(
            response,
            ('/auth/login/?next=/posts/1/edit/')
        )

    def test_post_edit_no_author(self):
        response = self.authorized_client1.get(
            self.private_test_username_post_edit,
            follow=True)
        self.assertRedirects(
            response, self.public_test_id_post)

    def test_urls_uses_correct_template(self):
        for url, template in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertTemplateUsed(response, template)
