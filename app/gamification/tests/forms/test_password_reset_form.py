from django.test import TestCase

from app.gamification.forms import PasswordResetForm


class PasswordResetFormTest(TestCase):
    fixtures = ['users.json']

    def test_form_with_existing_email(self):
        form = PasswordResetForm({'email': 'admin1@example.com '})
        self.assertTrue(form.is_valid())

    def test_form_with_non_existing_email(self):
        form = PasswordResetForm({'email': 'test@example.com '})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors.keys())
