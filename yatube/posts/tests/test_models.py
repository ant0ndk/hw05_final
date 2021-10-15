from django.test import TestCase
from posts.models import Post, Group
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


class TestGroupModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_title = 'Group_test'
        cls.group = Group.objects.create(
            title=cls.group_title,
            slug='aaa789',
            description='Тестовый текст!1!1'
        )
        cache.clear()

    def test_object_name_is_title_group(cls):
        group = Group.objects.all().first()
        expected_object_name = group.title
        cls.assertEqual(expected_object_name, str(cls.group_title),
                        '__str__ работает неверно')


class TestPostModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(username='aaaa',
                                   last_name='bbbb',
                                   email='aaa@zxc.net',
                                   password='bbbgFb789')
        cls.task = Post.objects.create(
            author=user,
            text='Тестовый текст',
        )

    def test_object_text_long(self):
        task = Post.objects.all().first()
        expected_object_name = task.text[:15]
        self.assertEqual(expected_object_name, str(task),
                         'Не проходит по ограничению поста в 15 символов')
