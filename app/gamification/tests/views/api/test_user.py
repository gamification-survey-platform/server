from django.test import TestCase
from django.urls import resolve, reverse

from app.gamification.models import CustomUser
from app.gamification.serializers import UserSerializer
from app.gamification.views.api import UserList, UserDetail


class RetrieveUserListTest(TestCase):

    def setUp(self):
        # Only admin users are allowed to hit the endpoint, so we need to create
        # a superuser first and login this user.
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
        }
        CustomUser.objects.create_superuser(**self.admin_data)
        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )

        self.url = reverse('user-list')
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, UserList.as_view().__name__)

    def test_response_content_type(self):
        '''
        Data in response should be in json format.
        '''
        self.assertEqual(self.response.get('content-type'), 'application/json')

    def test_response_data(self):
        '''
        Response should contain a list of users.
        '''
        data = self.response.json()

        # test the type of data
        self.assertIsInstance(data, list)
        # test the number of returned entries
        self.assertEqual(len(data), 1)
        # test the fields of each entry
        self.assertListEqual(list(data[0].keys()), UserSerializer.Meta.fields)
        # test the field data of a entry
        self.assertEqual(data[0].get('andrew_id'),
                         self.admin_data['andrew_id'])


class SuccessfullyCreateUserTest(TestCase):

    def setUp(self):
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
        }
        self.user_data = {
            'andrew_id': 'user',
            'password': 'user-password',
            'email': 'user@example.com',
        }

        CustomUser.objects.create_superuser(**self.admin_data)
        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )

        self.url = reverse('user-list')
        self.response = self.client.post(self.url, data=self.user_data)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 201)

    def test_url_resolves_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, UserList.as_view().__name__)

    def test_response_content_type(self):
        self.assertEqual(self.response.get('content-type'), 'application/json')

    def test_response_data(self):
        data = self.response.json()

        # test the type of data
        self.assertIsInstance(data, dict)
        # test the fields of each entry
        self.assertListEqual(list(data.keys()), UserSerializer.Meta.fields)
        # test the field data of a entry
        self.assertEqual(data.get('andrew_id'), self.user_data['andrew_id'])
        self.assertEqual(data.get('email'), self.user_data['email'])

    def test_user_creation(self):
        query_set = CustomUser.objects.filter(
            andrew_id=self.user_data['andrew_id'])
        self.assertTrue(query_set.exists())


class InvalidCreateUserTest(TestCase):

    def setUp(self):
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
        }
        self.user_data = {
            'andrew_id': 'user',
            'password': 'user-password',
            'email': 'user@example.com',
        }

        CustomUser.objects.create_superuser(**self.admin_data)

        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )
        self.url = reverse('user-list')

    def test_create_user_with_empty_andrew_id(self):
        # Arrange
        user_data_copy = self.user_data.copy()
        user_data_copy['andrew_id'] = ''
        # Act
        response = self.client.post(self.url, user_data_copy)
        # Assert
        self.assertEqual(response.status_code, 400)     # test response code
        self.assertIn('andrew_id', response.data)       # test response data
        query_set = CustomUser.objects.filter(
            andrew_id=self.user_data['andrew_id']).exists()
        self.assertFalse(query_set)                     # test user not created

    def test_create_user_with_no_andrew_id(self):
        # Arrange
        user_data_copy = self.user_data.copy()
        user_data_copy.pop('andrew_id')
        # Act
        response = self.client.post(self.url, user_data_copy)
        # Assert
        self.assertEqual(response.status_code, 400)     # test response code
        self.assertIn('andrew_id', response.data)       # test response data
        query_set = CustomUser.objects.filter(
            andrew_id=self.user_data['andrew_id']).exists()
        self.assertFalse(query_set)                     # test user not created

    def test_create_user_with_empty_email(self):
        # Arrange
        user_data_copy = self.user_data.copy()
        user_data_copy['email'] = ''
        # Act
        response = self.client.post(self.url, user_data_copy)
        # Assert
        self.assertEqual(response.status_code, 400)     # test response code
        self.assertIn('email', response.data)           # test response data
        query_set = CustomUser.objects.filter(
            andrew_id=self.user_data['andrew_id']).exists()
        self.assertFalse(query_set)                     # test user not created

    def test_create_user_with_no_email(self):
        # Arrange
        user_data_copy = self.user_data.copy()
        user_data_copy.pop('email')
        # Act
        response = self.client.post(self.url, user_data_copy)
        # Assert
        self.assertEqual(response.status_code, 400)     # test response code
        self.assertIn('email', response.data)           # test response data
        query_set = CustomUser.objects.filter(
            andrew_id=self.user_data['andrew_id']).exists()
        self.assertFalse(query_set)                     # test user not created


class UserListAuthenticationTest(TestCase):

    def setUp(self):
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
        }
        self.user_data = {
            'andrew_id': 'user',
            'password': 'user-password',
            'email': 'user@example.com',
        }
        self.post_data = {
            'andrew_id': 'post',
            'password': 'post-password',
            'email': 'post@example.com',
        }

        CustomUser.objects.create_superuser(**self.admin_data)
        CustomUser.objects.create_user(**self.user_data)

        self.url = reverse('user-list')

    def test_anonymous_user_cannot_get_data(self):
        # Act
        response = self.client.get(self.url)
        # Assert
        self.assertEqual(response.status_code, 403)

    def test_normal_user_cannot_get_data(self):
        # Arrange
        self.client.login(
            andrew_id=self.user_data['andrew_id'],
            password=self.user_data['password'],
        )
        # Act
        response = self.client.get(self.url)
        # Assert
        self.assertEqual(response.status_code, 403)

    def test_admin_user_can_get_data(self):
        # Arrange
        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )
        # Act
        response = self.client.get(self.url)
        # Assert
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_post_data(self):
        # Act
        response = self.client.post(self.url, self.post_data)
        # Assert
        self.assertEqual(response.status_code, 403)

    def test_normal_user_cannot_post_data(self):
        # Arrange
        self.client.login(
            andrew_id=self.user_data['andrew_id'],
            password=self.user_data['password'],
        )
        # Act
        response = self.client.post(self.url, self.post_data)
        # Assert
        self.assertEqual(response.status_code, 403)

    def test_admin_user_can_post_data(self):
        # Arrange
        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )
        # Act
        response = self.client.post(self.url, self.post_data)
        # Assert
        self.assertEqual(response.status_code, 201)


class RetrieveUserDetailTest(TestCase):

    def setUp(self):
        # Admin users are allowed to hit the endpoint, so we need to create
        # a superuser first and login this user.
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
        }
        CustomUser.objects.create_superuser(**self.admin_data)
        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )

        self.url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.admin_data['andrew_id']}
        )
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, UserDetail.as_view().__name__)

    def test_response_content_type(self):
        '''
        Data in response should be in json format.
        '''
        self.assertEqual(self.response.get('content-type'), 'application/json')

    def test_response_data(self):
        '''
        Response should contain a list of users.
        '''
        data = self.response.json()

        # test the type of data
        self.assertIsInstance(data, dict)
        # test the fields of each entry
        self.assertListEqual(list(data.keys()), UserSerializer.Meta.fields)
        # test the field data of a entry
        self.assertEqual(data.get('andrew_id'), self.admin_data['andrew_id'])


class SuccessfullyEditUserTest(TestCase):

    def setUp(self):
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
        }
        self.new_data = {
            'andrew_id': 'user',
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'user@example.com',
        }

        CustomUser.objects.create_superuser(**self.admin_data)
        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )

        self.url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.admin_data['andrew_id']}
        )
        self.response = self.client.put(
            self.url, data=self.new_data, content_type='application/json')

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, UserDetail.as_view().__name__)

    def test_response_content_type(self):
        self.assertEqual(self.response.get('content-type'), 'application/json')

    def test_response_data(self):
        data = self.response.json()

        # test the type of data
        self.assertIsInstance(data, dict)
        # test the fields of each entry
        self.assertListEqual(list(data.keys()), UserSerializer.Meta.fields)
        # test the field data of a entry
        self.assertEqual(data.get('andrew_id'), self.new_data['andrew_id'])
        self.assertEqual(data.get('email'), self.new_data['email'])

    def test_user_updated(self):
        user = CustomUser.objects.get(andrew_id=self.new_data['andrew_id'])

        self.assertEqual(user.andrew_id, self.new_data['andrew_id'])
        self.assertEqual(user.email, self.new_data['email'])
        self.assertEqual(user.first_name, self.new_data['first_name'])
        self.assertEqual(user.last_name, self.new_data['last_name'])


class InvalidEditUserTest(TestCase):

    def setUp(self):
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
        }
        self.new_data = {
            'andrew_id': 'user',
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'user@example.com',
        }

        CustomUser.objects.create_superuser(**self.admin_data)
        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )

        self.url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.admin_data['andrew_id']}
        )

    def test_edit_user_with_empty_andrew_id(self):
        # Arrange
        user_data_copy = self.new_data.copy()
        user_data_copy['andrew_id'] = ''
        # Act
        response = self.client.put(
            self.url, data=user_data_copy, content_type='application/json')
        # Assert
        self.assertEqual(response.status_code, 400)     # test response code
        self.assertIn('andrew_id', response.data)       # test response data
        query_set = CustomUser.objects.filter(
            andrew_id=self.new_data['andrew_id']).exists()
        self.assertFalse(query_set)                     # test user not updated

    def test_edit_user_with_no_andrew_id(self):
        # Arrange
        user_data_copy = self.new_data.copy()
        user_data_copy.pop('andrew_id')
        # Act
        response = self.client.put(
            self.url, data=user_data_copy, content_type='application/json')
        # Assert
        self.assertEqual(response.status_code, 400)     # test response code
        self.assertIn('andrew_id', response.data)       # test response data
        query_set = CustomUser.objects.filter(
            andrew_id=self.new_data['andrew_id']).exists()
        self.assertFalse(query_set)                     # test user not updated

    def test_edit_user_with_empty_email(self):
        # Arrange
        user_data_copy = self.new_data.copy()
        user_data_copy['email'] = ''
        # Act
        response = self.client.put(
            self.url, data=user_data_copy, content_type='application/json')
        # Assert
        self.assertEqual(response.status_code, 400)     # test response code
        self.assertIn('email', response.data)           # test response data
        query_set = CustomUser.objects.filter(
            andrew_id=self.new_data['andrew_id']).exists()
        self.assertFalse(query_set)                     # test user not updated

    def test_edit_user_with_no_email(self):
        # Arrange
        user_data_copy = self.new_data.copy()
        user_data_copy.pop('email')
        # Act
        response = self.client.put(
            self.url, data=user_data_copy, content_type='application/json')
        # Assert
        self.assertEqual(response.status_code, 400)     # test response code
        self.assertIn('email', response.data)           # test response data
        query_set = CustomUser.objects.filter(
            andrew_id=self.new_data['andrew_id']).exists()
        self.assertFalse(query_set)                     # test user not updated


class UserDetailAuthenticationTest(TestCase):

    def setUp(self):
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
        }
        self.user_data = {
            'andrew_id': 'user',
            'password': 'user-password',
            'email': 'user@example.com',
        }
        self.new_data = {
            'andrew_id': 'new',
            'password': 'new-password',
            'email': 'new@example.com',
        }

        CustomUser.objects.create_superuser(**self.admin_data)
        CustomUser.objects.create_user(**self.user_data)

    def test_anonymous_user_cannot_get_data(self):
        # Arrange
        url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.admin_data['andrew_id']}
        )
        # Act
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 403)

    def test_normal_user_cannot_get_other_user_data(self):
        # Arrange
        url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.admin_data['andrew_id']}
        )
        self.client.login(
            andrew_id=self.user_data['andrew_id'],
            password=self.user_data['password'],
        )
        # Act
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 403)

    def test_normal_user_can_get_his_own_data(self):
        # Arrange
        url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.user_data['andrew_id']}
        )
        self.client.login(
            andrew_id=self.user_data['andrew_id'],
            password=self.user_data['password'],
        )
        # Act
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 200)

    def test_admin_user_can_get_other_user_data(self):
        # Arrange
        url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.user_data['andrew_id']}
        )
        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )
        # Act
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 200)

    def test_admin_user_can_get_his_own_data(self):
        # Arrange
        url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.admin_data['andrew_id']}
        )
        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )
        # Act
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_edit_data(self):
        # Arrange
        url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.admin_data['andrew_id']}
        )
        # Act
        response = self.client.put(
            url, data=self.new_data, content_type='application/json')
        # Assert
        self.assertEqual(response.status_code, 403)

    def test_normal_user_cannot_edit_other_user_data(self):
        # Arrange
        url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.admin_data['andrew_id']}
        )
        self.client.login(
            andrew_id=self.user_data['andrew_id'],
            password=self.user_data['password'],
        )
        # Act
        response = self.client.put(
            url, data=self.new_data, content_type='application/json')
        # Assert
        self.assertEqual(response.status_code, 403)

    def test_normal_user_can_edit_his_own_data(self):
        # Arrange
        url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.user_data['andrew_id']}
        )
        self.client.login(
            andrew_id=self.user_data['andrew_id'],
            password=self.user_data['password'],
        )
        # Act
        response = self.client.put(
            url, data=self.new_data, content_type='application/json')
        # Assert
        self.assertEqual(response.status_code, 200)

    def test_admin_user_can_edit_other_user_data(self):
        # Arrange
        url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.user_data['andrew_id']}
        )
        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )
        # Act
        response = self.client.put(
            url, data=self.new_data, content_type='application/json')
        # Assert
        self.assertEqual(response.status_code, 200)

    def test_admin_user_can_edit_his_own_data(self):
        # Arrange
        url = reverse(
            'user-detail',
            kwargs={'andrew_id': self.admin_data['andrew_id']}
        )
        self.client.login(
            andrew_id=self.admin_data['andrew_id'],
            password=self.admin_data['password'],
        )
        # Act
        response = self.client.put(
            url, data=self.new_data, content_type='application/json')
        # Assert
        self.assertEqual(response.status_code, 200)
