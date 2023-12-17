def assert_note_fields_equal(self, note, form_data):
    self.assertEqual(note.title, form_data['title'])
    self.assertEqual(note.text, form_data['text'])
    self.assertEqual(note.slug, form_data['slug'])
