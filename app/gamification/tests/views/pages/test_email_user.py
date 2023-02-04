from django.core import mail
from django.test import TestCase
from django.urls import resolve, reverse

from app.gamification.views.pages import email_user


class EmailUserTest(TestCase):

    fixtures = ['users.json']

    def setUp(self):
        self.user_to_email = 'user1'
        self.url = reverse('email_user',
                           kwargs={'andrew_id': self.user_to_email})

    def test_url_resolves_email_user_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func, email_user)

    def test_successfully_email_user_and_redirect_next_page(self):
        # Arrange
        self.client.login(andrew_id='admin1', password='admin1-password')
        redirect_url = reverse('profile')
        # Act
        response = self.client.post(self.url, {'next': redirect_url})
        # Assert
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Gamification', mail.outbox[0].subject)
        self.assertIn(self.user_to_email, mail.outbox[0].body)
        self.assertRedirects(response, redirect_url)

    def test_post_method_without_defining_next_page(self):
        # Arrange
        self.client.login(andrew_id='admin1', password='admin1-password')
        default_redirect_url = reverse('dashboard')
        # Act
        response = self.client.post(self.url)
        # Assert
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Gamification', mail.outbox[0].subject)
        self.assertIn(self.user_to_email, mail.outbox[0].body)
        self.assertRedirects(response, default_redirect_url)

    def test_get_method_does_nothing(self):
        # Arrange
        self.client.login(andrew_id='admin1', password='admin1-password')
        redirect_url = reverse('dashboard')
        # Act
        response = self.client.get(self.url, {'next': redirect_url})
        # Assert
        self.assertEqual(len(mail.outbox), 0)
        self.assertRedirects(response, redirect_url)

    def test_get_method_without_defining_next_page(self):
        # Arrange
        self.client.login(andrew_id='admin1', password='admin1-password')
        default_redirect_url = reverse('dashboard')
        # Act
        response = self.client.get(self.url)
        # Assert
        self.assertEqual(len(mail.outbox), 0)
        self.assertRedirects(response, default_redirect_url)
