from django.test import TestCase
from django.urls import resolve, reverse

from app.gamification.models import Course, CustomUser
from app.gamification.serializers import CourseSerializer
from app.gamification.views.api.course import CourseList, CourseDetail


class RetrieveCourseListTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            course_id='12345',
            course_name='Test Course',
            syllabus='Test Syllabus',
            semester='Fall',
            visible=True
        )

        self.url = reverse('course-list')
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, CourseList.as_view().__name__)

    def test_response_content_type(self):
        self.assertEqual(self.response.get('content-type'), 'application/json')

    def test_response_data(self):
        '''
        Response should contain a list of courses.
        '''
        data = self.response.json()

        # test the type of data
        self.assertIsInstance(data, list)
        # test the number of returned entries
        self.assertEqual(len(data), 1)
        # test the fields of each entry
        self.assertListEqual(
            list(data[0].keys()), CourseSerializer.Meta.fields)
        # test the field data of a entry
        self.assertEqual(data[0].get('course_id'), self.course.course_id)

        serializer = CourseSerializer(self.course)
        self.assertDictEqual(data[0], serializer.data)


class SuccessfullyCreateCourseTest(TestCase):

    def setUp(self):
        self.data = {
            'course_id': '12345',
            'course_name': 'Test Course',
            'syllabus': 'Test Syllabus',
            'semester': 'Fall',
            'visible': True
        }

        admin_andrew_id = 'admin'
        admin_password = 'admin-password'
        CustomUser.objects.create_superuser(
            andrew_id=admin_andrew_id, password=admin_password
        )
        self.client.login(username=admin_andrew_id, password=admin_password)

        self.url = reverse('course-list')
        self.response = self.client.post(self.url, data=self.data)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 201)

    def test_url_resolves_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, CourseList.as_view().__name__)

    def test_response_content_type(self):
        self.assertEqual(self.response.get('content-type'), 'application/json')

    def test_response_data(self):
        data = self.response.json()

        # test the type of data
        self.assertIsInstance(data, dict)
        # test the fields of each entry
        self.assertListEqual(
            list(data.keys()), CourseSerializer.Meta.fields)
        # test the field data of a entry
        self.assertEqual(data.get('course_id'), self.data.get('course_id'))

        serializer = CourseSerializer(Course.objects.get(id=data.get('id')))
        self.assertDictEqual(data, serializer.data)

    def test_course_creation(self):
        queryset = Course.objects.filter(course_id=self.data['course_id'])
        self.assertTrue(queryset.exists())
        self.assertEqual(Course.objects.count(), 1)


class CourseListAuthenticationTest(TestCase):

    def setUp(self):
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
            'email': 'admin@example.com',
        }
        self.user_data = {
            'andrew_id': 'user',
            'password': 'user-password',
            'email': 'user@example.com',
        }
        self.post_data = {
            'course_id': '12345',
            'course_name': 'Test Course',
            'syllabus': 'Test Syllabus',
            'semester': 'Fall',
            'visible': True,
        }

        CustomUser.objects.create_superuser(**self.admin_data)
        CustomUser.objects.create_user(**self.user_data)

        self.url = reverse('course-list')

    def test_anonymous_user_can_get_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_normal_user_can_get_data(self):
        self.client.login(**self.user_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_admin_user_can_get_data(self):
        self.client.login(**self.admin_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_post_data(self):
        response = self.client.post(self.url, data=self.post_data)
        self.assertEqual(response.status_code, 403)

    def test_normal_user_cannot_post_data(self):
        self.client.login(**self.user_data)
        response = self.client.post(self.url, data=self.post_data)
        self.assertEqual(response.status_code, 403)

    def test_admin_user_can_post_data(self):
        self.client.login(**self.admin_data)
        response = self.client.post(self.url, data=self.post_data)
        self.assertEqual(response.status_code, 201)


class RetrieveCourseDetailTest(TestCase):

    def setUp(self):
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
        }
        CustomUser.objects.create_superuser(**self.admin_data)
        self.client.login(**self.admin_data)

        self.course = Course.objects.create(
            course_id='12345',
            course_name='Test Course',
            syllabus='Test Syllabus',
            semester='Fall',
            visible=True
        )

        self.url = reverse('course-detail', kwargs={'id': 1})
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, CourseDetail.as_view().__name__)

    def test_response_content_type(self):
        self.assertEqual(self.response.get('content-type'), 'application/json')

    def test_response_data(self):
        data = self.response.json()

        # test the type of data
        self.assertIsInstance(data, dict)
        # test the fields of each entry
        self.assertListEqual(list(data.keys()), CourseSerializer.Meta.fields)
        # test the field data of a entry
        self.assertEqual(data.get('course_id'), self.course.course_id)

        serializer = CourseSerializer(self.course)
        self.assertDictEqual(data, serializer.data)


class SuccessfullyEditCourseTest(TestCase):

    def setUp(self):
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
        }
        CustomUser.objects.create_superuser(**self.admin_data)
        self.client.login(**self.admin_data)

        data = {
            'course_id': '12345',
            'course_name': 'Test Course',
            'syllabus': 'Test Syllabus',
            'semester': 'Fall',
            'visible': True,
        }
        Course.objects.create(**data)

        self.url = reverse('course-detail', kwargs={'id': 1})
        self.new_data = {'course_id': '54321'}
        self.response = self.client.put(
            self.url, data=self.new_data, content_type='application/json')

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, CourseDetail.as_view().__name__)

    def test_response_content_type(self):
        self.assertEqual(self.response.get('content-type'), 'application/json')

    def test_response_data(self):
        data = self.response.json()
        # test the type of data
        self.assertIsInstance(data, dict)
        # test the fields of each entry
        self.assertListEqual(list(data.keys()), CourseSerializer.Meta.fields)
        # test the field data of a entry
        self.assertEqual(data.get('course_id'), self.new_data.get('course_id'))

        serializer = CourseSerializer(Course.objects.get(id=1))
        self.assertDictEqual(data, serializer.data)

    def test_course_updated(self):
        course = Course.objects.get(id=1)
        self.assertEqual(course.course_id, self.new_data.get('course_id'))


class CourseDetailAuthenticationTest(TestCase):

    def setUp(self):
        self.admin_data = {
            'andrew_id': 'admin',
            'password': 'admin-password',
            'email': 'admin@example.com',
        }
        self.user_data = {
            'andrew_id': 'user',
            'password': 'user-password',
            'email': 'user@example.com',
        }

        CustomUser.objects.create_superuser(**self.admin_data)
        CustomUser.objects.create_user(**self.user_data)

        self.data = {
            'course_id': '12345',
            'course_name': 'Test Course',
            'syllabus': 'Test Syllabus',
            'semester': 'Fall',
            'visible': True,
        }
        self.new_data = {
            'course_id': '54321',
        }

        Course.objects.create(**self.data)

        self.url = reverse('course-detail', kwargs={'id': 1})

    def test_anonymous_user_cannot_get_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_normal_user_cannot_get_data(self):
        self.client.login(**self.user_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_admin_user_can_get_data(self):
        self.client.login(**self.admin_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_edit_data(self):
        response = self.client.put(
            self.url, data=self.new_data, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_normal_user_cannot_edit_data(self):
        self.client.login(**self.user_data)
        response = self.client.put(
            self.url, data=self.new_data, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_admin_user_can_edit_data(self):
        self.client.login(**self.admin_data)
        response = self.client.put(
            self.url, data=self.new_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
