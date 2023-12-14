from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    user = None
    user_client = None

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testUser')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.notes = Note.objects.create(title='Заголовок', text='Текст',
                                        slug='',
                                        author=cls.user)
        cls.reader = User.objects.create(username='Читатель простой')

    def test_successful_creation(self):
        news_count = Note.objects.count()
        self.assertEqual(news_count, 1)

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_create_and_list_and_success_pages(self):
        pages = [
            {'url': reverse('notes:add'), 'expected_status': 200},
            {'url': reverse('notes:success'), 'expected_status': 200},
            {'url': reverse('notes:list'), 'expected_status': 200}
        ]

        for page in pages:
            response = self.user_client.get(page['url'])
            self.assertEqual(response.status_code, page['expected_status'])

    def test_detail_page(self):
        url = reverse('notes:detail', kwargs={'slug': self.notes.slug})
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.notes.title)
        self.assertContains(response, self.notes.text)
        self.assertContains(response, self.notes.author.username)
        self.assertContains(response, self.notes.slug)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.user, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name, args in (('notes:list', None),
                           ('notes:success', None),
                           ('notes:add', None),
                           ('notes:edit', (self.notes.slug,)),
                           ('notes:delete', (self.notes.slug,)),
                           ('notes:detail', (self.notes.slug,))):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
