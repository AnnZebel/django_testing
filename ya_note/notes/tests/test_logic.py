from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note
from notes.tests.utils import assertnotefieldsequal

User = get_user_model()


class BaseTestCase(TestCase):

    author = None
    author_client = None

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }


class TestLogic(BaseTestCase):

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        initial_count = Note.objects.count()
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.exists(), False)

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        self.note = Note.objects.create(title='Заголовок', text='Текст',
                                        slug='note-slug', author=self.author)
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertTrue(Note.objects.exists())

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertTrue(Note.objects.exists())
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(BaseTestCase):

    author = None
    form_data = {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    }

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_author_can_edit_note(self):
        client = Client()
        client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        assertnotefieldsequal(self, self.note, self.form_data)

    def test_other_user_cant_edit_note(self):
        admin = User.objects.create(username='Админ')
        client = Client()
        client.force_login(admin)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, 404)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        client = Client()
        client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertFalse(Note.objects.exists())

    def test_other_user_cant_delete_note(self):
        admin = User.objects.create(username='Админ')
        client = Client()
        client.force_login(admin)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.exists())
