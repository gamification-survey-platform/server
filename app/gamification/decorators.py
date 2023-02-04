from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import resolve_url

from app.gamification.models import Course, Registration


def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME, **decorator_kwargs):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and possibly other arguments and returns True 
    if the user passes.

    This decorator comes from the Django 3.2 docs.
    """

    def decorator(view_func):

        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            test_func_kwargs = {}
            test_func_kwargs.update(decorator_kwargs)
            test_func_kwargs.update(kwargs)

            if test_func(request.user, **test_func_kwargs):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)

        return _wrapped_view

    return decorator


def admin_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the logged in user is a staff member,
    redirecting to the log-in page if necessary.
    """
    def func(user, **kwargs):
        return user.is_staff
    
    actual_decorator = user_passes_test(
        func,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def user_role_check(user_roles, raise_exception=True):
    """
    Check if user is instructor or student in course.
    """

    if isinstance(user_roles, str):
        user_roles = [user_roles]

    def func(user, course_id, user_roles, **kwargs):
        if user.is_staff:
            return True

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise Http404("Course does not exist.")

        try:
            registration = Registration.objects.get(
                users=user, courses=course)
            if registration.userRole in user_roles:
                return True
        except Registration.DoesNotExist:
            pass

        if raise_exception:
            raise PermissionDenied

        return False

    actual_decorator = user_passes_test(
        func,
        login_url=None,
        redirect_field_name=None,
        user_roles=user_roles
    )

    return actual_decorator
