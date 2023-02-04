from django.test import TestCase
from django.urls import resolve, reverse

from app.gamification.views.pages import instructor_admin
from app.gamification.tests.views.pages.utils import LogInUser


class InstructorAdminTest(TestCase):

    def setUp(self):
        test_andrew_id = 'andrew_id'
        test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id, test_password, is_superuser=True)
        self.url = reverse('instructor_admin')
        self.response = self.client.get(self.url)

    def test_response_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_resolves_correct_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func, instructor_admin)


class InstructorAdminAuthenticationTest(TestCase):

    def setUp(self):
        self.normal_andrew_id = 'andrew_id'
        self.normal_password = '1234'
        self.admin_andrew_id = 'admin_andrew_id'
        self.admin_password = '1234'

        self.normal_user = LogInUser.create_user(
            andrew_id=self.normal_andrew_id,
            password=self.normal_password,
        )
        self.admin_user = LogInUser.create_user(
            andrew_id=self.admin_andrew_id,
            password=self.admin_password,
            is_superuser=True,
        )

        self.url = reverse('instructor_admin')

    def test_normal_user_will_be_redirected(self):
        '''A normal user should not be able to view the admin page.'''
        # Arrange
        self.client.login(andrew_id=self.normal_andrew_id,
                          password=self.normal_password)
        # Act
        response = self.client.get(self.url)
        # Assert
        self.assertRedirects(response, reverse('dashboard'))

    def test_admin_user_can_view_admin_page(self):
        '''An admin user should be able to view the admin page.'''
        # Arrange
        self.client.login(andrew_id=self.admin_andrew_id,
                          password=self.admin_password)
        # Act
        response = self.client.get(self.url)
        # Assert
        self.assertEqual(response.status_code, 200)
