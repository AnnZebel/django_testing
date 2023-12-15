from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy

from notes.models import Note
from notes import forms

User = get_user_model()

USERNAME = 'testuser'
SECOND_USERNAME = 'testuser1'


class TestContent(TestCase):

    user = None

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create(username=USERNAME)
        cls.second_user = User.objects.create(username=SECOND_USERNAME)
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       slug='note-slug',
                                       author=cls.user)

    def setUp(self):
        self.client.force_login(self.user)

    def test_single_note_passed_to_notes_list(self):
        response = self.client.get(reverse_lazy('notes:list'))
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertEqual(response.context['object_list'][0], self.note)

    def test_notes_of_one_user_not_displayed_to_another_user(self):
        self.client.logout()
        self.client.force_login(self.second_user)
        response = self.client.get(reverse_lazy('notes:list'))
        self.assertEqual(len(response.context['object_list']), 0)

    def test_forms_passed_to_note_creation_and_editing_pages(self):
        response = self.client.get(reverse_lazy('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], forms.NoteForm)
        response = self.client.get(reverse_lazy
                                   ('notes:edit',
                                    kwargs={'slug': self.note.slug}))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], forms.NoteForm)
