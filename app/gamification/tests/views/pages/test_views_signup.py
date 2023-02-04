from django.test import TestCase
from django.urls import resolve, reverse

from app.gamification.forms import SignUpForm
from app.gamification.models import CustomUser
from app.gamification.views.pages import signup


class SignUpTest(TestCase):

    def setUp(self):
        self.url = reverse('signup')
        self.response = self.client.get(self.url)

    def test_signup_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func, signup)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)

    def test_form_inputs(self):
        '''
        The view must contain five inputs: csrf, andrew_id, email, password1, password2
        '''
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'name="andrew_id"', 1)
        self.assertContains(self.response, 'name="email"', 1)
        self.assertContains(self.response, 'name="password1"', 1)
        self.assertContains(self.response, 'name="password2"', 1)


class SuccessfulSignUpTest(TestCase):

    def setUp(self):
        self.url = reverse('signup')
        self.data = {
            'andrew_id': 'alice',
            'email': 'alice@example.com',
            'password1': 'arbitary-password',
            'password2': 'arbitary-password',
        }
        self.response = self.client.post(self.url, self.data)
        self.profile_url = reverse('profile')

    def test_redirection(self):
        '''
        A valid form submission should redirect the user to profile page
        '''
        self.assertRedirects(self.response, self.profile_url)

    def test_user_creation(self):
        # Act
        query_set = CustomUser.objects.filter(andrew_id='alice')
        # Assert
        self.assertTrue(query_set.exists())

    def test_user_authentication(self):
        '''
        Create a new request to an arbitary page.
        The resulting response should now have an 'user' to its context, after
        a successful sign up.
        '''

        # Arrange
        response = self.client.get(self.profile_url)
        # Act
        user = response.context.get('user')
        # Assert
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.andrew_id, 'alice')


class InvalidSignUpTest(TestCase):

    def setUp(self):
        self.url = reverse('signup')
        self.data = {
            'andrew_id': 'alice',
            'email': 'alice@example.com',
            'password1': 'arbitary-password',
            'password2': 'arbitary-password',
        }

    def test_signup_with_no_andrew_id(self):
        # Arrange
        self.data['andrew_id'] = ''
        # Act
        response = self.client.post(self.url, self.data)
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)     # test response code
        self.assertIn('andrew_id', form.errors.keys())  # test form error field
        self.assertFalse(CustomUser.objects.exists())   # test user not created

    def test_signup_with_too_long_andrew_id(self):
        # Arrange
        self.data['andrew_id'] = ''.join(['a'] * 200)
        # Act
        response = self.client.post(self.url, self.data)
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)     # test response code
        self.assertIn('andrew_id', form.errors.keys())  # test form error field
        self.assertFalse(CustomUser.objects.exists())   # test user not created

    def test_signup_with_no_email(self):
        # Arrange
        self.data['email'] = ''
        # Act
        response = self.client.post(self.url, self.data)
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)     # test response code
        self.assertIn('email', form.errors.keys())      # test form error field
        self.assertFalse(CustomUser.objects.exists())   # test user not created

    def test_signup_with_no_password(self):
        # Arrange
        self.data['password1'] = ''
        # Act
        response = self.client.post(self.url, self.data)
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)     # test response code
        self.assertIn('password1', form.errors.keys())  # test form error field
        self.assertFalse(CustomUser.objects.exists())   # test user not created

    def test_signup_with_no_confirm_password(self):
        # Arrange
        self.data['password2'] = ''
        # Act
        response = self.client.post(self.url, self.data)
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)     # test response code
        self.assertIn('password2', form.errors.keys())  # test form error field
        self.assertFalse(CustomUser.objects.exists())   # test user not created

    def test_signup_with_password_mismatching_confirm_password(self):
        # Arrange
        self.data['password1'] = 'new-password'
        self.data['password2'] = 'old-password'
        # Act
        response = self.client.post(self.url, self.data)
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)     # test response code
        self.assertIn('password2', form.errors.keys())  # test form error field
        self.assertFalse(CustomUser.objects.exists())   # test user not created

    def test_signup_with_too_short_password(self):
        # Arrange
        self.data['password1'] = 'abc123'
        self.data['password2'] = 'abc123'
        # Act
        response = self.client.post(self.url, self.data)
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)     # test response code
        self.assertIn('password1', form.errors.keys())  # test form error field
        self.assertFalse(CustomUser.objects.exists())   # test user not created

    def test_signup_with_password_similar_to_andrew_id(self):
        # Arrange
        self.data['password1'] = self.data['andrew_id']
        self.data['password2'] = self.data['andrew_id']
        # Act
        response = self.client.post(self.url, self.data)
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)     # test response code
        self.assertIn('password1', form.errors.keys())  # test form error field
        self.assertFalse(CustomUser.objects.exists())   # test user not created

    def test_signup_with_too_common_password(self):
        # Arrange
        self.data['password1'] = 'password'
        self.data['password2'] = 'password'
        # Act
        response = self.client.post(self.url, self.data)
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)     # test response code
        self.assertIn('password1', form.errors.keys())  # test form error field
        self.assertFalse(CustomUser.objects.exists())   # test user not created

    def test_signup_with_entirely_numeric_password(self):
        # Arrange
        self.data['password1'] = '20220324'
        self.data['password2'] = '20220324'
        # Act
        response = self.client.post(self.url, self.data)
        form = response.context.get('form')
        # Assert
        self.assertEqual(response.status_code, 200)     # test response code
        self.assertIn('password1', form.errors.keys())  # test form error field
        self.assertFalse(CustomUser.objects.exists())   # test user not created
