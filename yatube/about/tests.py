from django.test import Client, TestCase
from django.urls import reverse


class AboutPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_tech_url_exists_at_desired_location(self):
        """Проверка доступности адресов author и tech."""
        urls_names = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for address, status_code in urls_names.items():
            with self.subTest(status_code=status_code):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_about_urls_uses_correct_template(self):
        """Проверка шаблона для адресов author и tech."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template(self):
        """VIEW-функции используют соответствующие шаблоны."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
