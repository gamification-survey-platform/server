from django.contrib.auth.views import PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView
from django.test import TestCase
from django.urls import resolve, reverse

from app.gamification.forms import PasswordResetForm
from app.gamification.views.pages import PasswordResetView


class PasswordResetTest(TestCase):

    def test_password_reset_view_resolves_correct_view(self):
        url = reverse('password_reset')
        view = resolve(url)
        self.assertEqual(view.func.__name__,
                         PasswordResetView.as_view().__name__)

    def test_password_reset_view_uses_custom_template(self):
        url = reverse('password_reset')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'password_reset.html')

    def test_password_reset_view_uses_custom_form(self):
        url = reverse('password_reset')
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, PasswordResetForm)

    def test_password_reset_done_sent_view_resolves_correct_view(self):
        url = reverse('password_reset_done')
        view = resolve(url)
        self.assertEqual(view.func.__name__,
                         PasswordResetDoneView.as_view().__name__)

    def test_password_reset_done_sent_view_uses_custom_template(self):
        url = reverse('password_reset_done')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'password_reset_done.html')

    def test_password_reset_confirm_view_resolves_correct_view(self):
        url = reverse('password_reset_confirm', kwargs={
                      'uidb64': '12345', 'token': '12345'})
        view = resolve(url)
        self.assertEqual(view.func.__name__,
                         PasswordResetConfirmView.as_view().__name__)

    def test_password_reset_confirm_view_uses_custom_template(self):
        url = reverse('password_reset_confirm', kwargs={
                      'uidb64': '12345', 'token': '12345'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'password_reset_confirm.html')

    def test_password_reset_complete_view_resolves_correct_view(self):
        url = reverse('password_reset_complete')
        view = resolve(url)
        self.assertEqual(view.func.__name__,
                         PasswordResetCompleteView.as_view().__name__)

    def test_password_reset_complete_view_uses_custom_template(self):
        url = reverse('password_reset_complete')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'password_reset_complete.html')
