from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class TestAboutAvailable(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_status_codes(self):
        url_names = ['/about/author/', '/about/tech/']
        for url in url_names:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, 200)


class TestAboutUrls(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_correct_templates_usage(self):
        templates_and_urls = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, reverse_name in templates_and_urls.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
