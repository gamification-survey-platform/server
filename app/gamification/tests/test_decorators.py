from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.urls import path, reverse

from app.gamification.decorators import admin_required, user_role_check
from app.gamification.models import Course, CustomUser, Registration


# Special views for decorator tests
def dashboard(request):
    return HttpResponse()


def view(request):
    return HttpResponse()


# Special urls for decorator tests
urlpatterns = [
    path('dashboard/', view, name='dashboard'),
    path('admin_required/', admin_required(view)),
    path('admin_required_redirect_url/',
         admin_required(view, login_url='/dashboard/')),
]


@override_settings(ROOT_URLCONF='app.gamification.tests.test_decorators')
class AdminRequiredTest(TestCase):
    '''
    Test the admin_required decorator.

    This test code is based on the code from the following URL:
    https://github.com/django/django/blob/stable%2F3.2.x/tests/auth_tests/test_decorators.py
    '''

    fixtures = ['users.json']

    @classmethod
    def setUpTestData(self):
        self.normal_andrew_id = 'user1'
        self.normal_password = 'suer1-password'
        self.admin_andrew_id = 'admin1'
        self.admin_password = 'admin1-password'

    def test_callable(self):
        '''
        login_required is assignable to callable objects.
        '''
        class CallableView:
            def __call__(self, *args, **kwargs):
                pass
        admin_required(CallableView())

    def test_view(self):
        '''
        login_required is assignable to normal views.
        '''
        def normal_view(request):
            pass
        admin_required(normal_view)

    def test_normal_user_will_be_redirected(self, view_url='/admin_required/', redirect_url=None):
        '''
        Normal user will be redirected to other page.
        '''
        # Arrange
        if redirect_url is None:
            redirect_url = settings.LOGIN_URL
        self.client.login(andrew_id=self.normal_andrew_id,
                          password=self.normal_password)

        # Act
        response = self.client.get(view_url)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertIn(redirect_url, response.url)

    def test_redirect_url(self, view_url='/admin_required_redirect_url/', redirect_url='/dashboard/'):
        '''
        Redirect url can be specified.
        '''
        self.test_normal_user_will_be_redirected(view_url, redirect_url)

    def test_admin_user_can_visit(self, view_url='/admin_required/', redirect_url=None):
        '''
        Normal user will be redirected to other page.
        '''
        # Arrange
        if redirect_url is None:
            redirect_url = reverse('dashboard')
        self.client.login(andrew_id=self.admin_andrew_id,
                          password=self.admin_password)

        # Act
        response = self.client.get(view_url)

        # Assert
        self.assertEqual(response.status_code, 200)


class UserRoleCheckDecoratorTest(TestCase):
    '''
    Tests for the user_role_check decorator.

    This test code is based on the code from the following URL:
    https://github.com/django/django/blob/stable%2F3.2.x/tests/auth_tests/test_decorators.py
    '''

    fixtures = ['users.json', 'courses.json', 'registration.json']

    factory = RequestFactory()

    @classmethod
    def setUpTestData(self):
        self.student_andrew_id = 'user1'
        self.student_password = 'user1-password'
        self.ta_andrew_id = 'user4'
        self.ta_password = 'user4-password'
        self.instructor_andrew_id = 'admin1'
        self.instructor_password = 'admin1-password'
        self.admin_andrew_id = 'admin2'
        self.admin_password = 'admin2-password'

        self.course = Course.objects.get(
            course_number='18652', semester='Fall 2021'
        )

        self.student = CustomUser.objects.get(andrew_id=self.student_andrew_id)
        self.ta = CustomUser.objects.get(andrew_id=self.ta_andrew_id)
        self.instructor = CustomUser.objects.get(
            andrew_id=self.instructor_andrew_id)
        self.admin = CustomUser.objects.get(andrew_id=self.admin_andrew_id)

    def test_student_role_check_passed(self):
        '''
        Student role check passed.
        '''
        # Arrange
        @user_role_check(user_roles=Registration.UserRole.Student)
        def test_view(request, course_id):
            return HttpResponse()

        request = self.factory.get('/random/')
        request.user = self.student

        # Act
        response = test_view(request, course_id=self.course.pk)

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_student_role_check_failed(self):
        '''
        Student role check failed.
        '''
        # Arrange
        @user_role_check(user_roles=Registration.UserRole.TA)
        def test_view(request, course_id):
            return HttpResponse()

        request = self.factory.get('/random/')
        request.user = self.student

        # Act & Assert
        with self.assertRaises(PermissionDenied):
            test_view(request, course_id=self.course.pk)

    def test_ta_role_check_passed(self):
        '''
        TA role check passed.
        '''
        # Arrange
        @user_role_check(user_roles=Registration.UserRole.TA)
        def test_view(request, course_id):
            return HttpResponse()

        request = self.factory.get('/random/')
        request.user = self.ta

        # Act
        response = test_view(request, course_id=self.course.pk)

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_ta_role_check_failed(self):
        '''
        TA role check failed.
        '''
        # Arrange
        @user_role_check(user_roles=Registration.UserRole.Student)
        def test_view(request, course_id):
            return HttpResponse()

        request = self.factory.get('/random/')
        request.user = self.ta

        # Act & Assert
        with self.assertRaises(PermissionDenied):
            test_view(request, course_id=self.course.pk)

    def test_instructor_role_check_passed(self):
        '''
        Instructor role check passed.
        '''
        # Arrange
        @user_role_check(user_roles=Registration.UserRole.Instructor)
        def test_view(request, course_id):
            return HttpResponse()

        request = self.factory.get('/random/')
        request.user = self.instructor

        # Act
        response = test_view(request, course_id=self.course.pk)

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_admin_role_check_passed(self):
        '''
        Admin role check passed.
        '''
        # Arrange
        @user_role_check(user_roles=Registration.UserRole.TA)
        def test_view(request, course_id):
            return HttpResponse()

        request = self.factory.get('/random/')
        request.user = self.admin

        # Act
        response = test_view(request, course_id=self.course.pk)

        # Assert
        self.assertEqual(response.status_code, 200)
