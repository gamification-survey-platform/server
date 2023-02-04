import shutil
import os
from django.test import TestCase
from django.urls import resolve, reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from app.gamification.forms import ProfileForm
from app.gamification.views.pages import profile
from app.gamification.tests.views.pages.utils import LogInUser
from django.conf import settings

"""Test the profile view.
    -  Using ? of:
        - User Type: not logged in, logged in as student, logged in as instructor, logged in as admin
        - Profile Image Type: with picture, without picture
        - email: with andrew email, without andrew email
"""


class ProfileTest(TestCase):

    def setUp(self):
        test_andrew_id = 'andrew_id'
        test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id, test_password)
        self.url = reverse('profile')
        self.response = self.client.get(self.url)

    def test_profile_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_profile_url_resolves_profile_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func, profile)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, ProfileForm)

    def test_form_inputs(self):
        '''
        The view must contain four inputs: csrf, andrew_id, email, first_name, last_name, image
        '''
        self.assertContains(self.response, 'name="email"', 1)
        self.assertContains(self.response, 'name="first_name"', 1)
        self.assertContains(self.response, 'name="last_name"', 1)
        self.assertContains(self.response, 'name="image"', 1)


class SuccessfulEditProfileTest(TestCase):

    def setUp(self):
        if(os.path.exists(settings.MEDIA_ROOT)):
            shutil.rmtree(settings.MEDIA_ROOT)

        self.test_andrew_id = 'andrew_id'
        self.test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, self.test_andrew_id, self.test_password)

        filepath = settings.STATICFILES_DIRS[0] / 'images/faces/face1.jpg'
        f = open(filepath, 'rb')
        uploaded_image = SimpleUploadedFile(
            name=filepath,
            content=f.read(),
            content_type='image/jpg'
        )
        self.data = {
            'email': 'alice@example.com',
            'first_name': 'Alex',
            'last_name': 'He',
            'image': uploaded_image
        }

        self.url = reverse('profile')
        self.response = self.client.post(self.url, data=self.data)

    def tearDown(self):
        # Remove MEDIA directory after tests finish
        if(os.path.exists(settings.MEDIA_ROOT)):
            shutil.rmtree(settings.MEDIA_ROOT)

    def test_user_info_updated(self):
        # Arrange
        response = self.client.get(self.url)
        # Act
        user = response.context.get('user')
        # Assert
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(user.andrew_id, self.test_andrew_id)
        self.assertEqual(user.email, 'alice@example.com')
        self.assertEqual(user.first_name, 'Alex')
        self.assertEqual(user.last_name, 'He')
        self.assertEqual(
            str(settings.MEDIA_ROOT / 'profile_pics/face1.jpg'),  user.image.path)


class InvalidEditProfileTest(TestCase):

    def setUp(self):
        if(os.path.exists(settings.MEDIA_ROOT)):
            shutil.rmtree(settings.MEDIA_ROOT)

        self.test_andrew_id = 'andrew_id'
        self.test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, self.test_andrew_id, self.test_password)

        self.url = reverse('profile')
        filepath = settings.STATICFILES_DIRS[0] / 'images/faces/face1.jpg'
        f = open(filepath, 'rb')
        uploaded_image = SimpleUploadedFile(
            name=filepath,
            content=f.read(),
            content_type='image/jpg'
        )

        self.data = {
            'email': 'alice@example.com',
            'first_name': 'Tom',
            'last_name': 'James',
            'image': uploaded_image,

        }
        # self.response = self.client.post(self.url, self.data)

    def tearDown(self):
        # Remove MEDIA directory after tests finish
        if(os.path.exists(settings.MEDIA_ROOT)):
            shutil.rmtree(settings.MEDIA_ROOT)

    def test_edit_profile_with_no_email(self):
        # Arrange
        self.data['email'] = ''
        # Act
        response = self.client.post(self.url, self.data)
        user = response.context.get('user')
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', form.errors.keys())

    def test_edit_profile_with_no_firstname(self):
        # Arrange
        self.data['first_name'] = ''
        # Act
        response = self.client.post(self.url, self.data)
        user = response.context.get('user')
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.first_name, '')

    def test_edit_profile_with_no_lastname(self):
        # Arrange
        self.data['last_name'] = ''
        # Act
        response = self.client.post(self.url, self.data)
        user = response.context.get('user')
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.last_name, '')

    def test_edit_profile_with_no_image(self):
        # Arrange
        self.data['image'] = ''
        # Act
        response = self.client.post(self.url, self.data)
        user = response.context.get('user')
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.image, '')

    def test_edit_profile_with_anonymous_user(self):
        # Arrange
        signin_url = reverse('signin')
        redirect_url = "%s?next=%s" % (signin_url, self.url)
        self.client.logout()
        # Act
        response = self.client.post(self.url, self.data)
        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_edit_profile_with_invalid_type_of_file(self):
        # Arrange
        filepath = settings.STATICFILES_DIRS[0] / 'images/faces/face1.pdf'
        f = open(filepath, 'rb')
        uploaded_image = SimpleUploadedFile(
            name=filepath,
            content=f.read(),
            content_type='application/pdf'
        )
        self.data['image'] = uploaded_image
        # Act
        response = self.client.post(self.url, self.data)
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('image', form.errors.keys())
