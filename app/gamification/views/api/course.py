from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from app.gamification.models import Course, Registration, CustomUser
from app.gamification.utils.auth import get_user_pk
from app.gamification.serializers import CourseSerializer, RegistrationSerializer
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class IsAdminOrReadOnly(permissions.BasePermission):
    '''
    Custom permission to only allow users to view read-only information.
    Admin users are allowed to view and edit information.
    '''

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class CourseDetail(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get course information",
        tags=['courses'],
        responses={
            200: openapi.Response(
                description='Course information',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'course_number': openapi.Schema(type=openapi.TYPE_STRING),
                        'course_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'syllabus': openapi.Schema(type=openapi.TYPE_STRING),
                        'semester': openapi.Schema(type=openapi.TYPE_STRING),
                        'visible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'picture': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def get(self, request, course_id, *args, **kwargs):
        andrew_id = get_user_pk(request)
        user = CustomUser.objects.get(andrew_id=andrew_id)
        course = get_object_or_404(Course, pk=course_id)
        registration = get_object_or_404(
            Registration, user=user, course=course)
        if course.visible == False and registration.userRole == Registration.UserRole.Student:
            # return 403 and error message
            content = {'message': 'Permission denied'}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        serializer = CourseSerializer(course)
        response_data = serializer.data
        response_data['points'] = registration.points
        response_data['userRole'] = registration.userRole

        return Response(response_data)

    @swagger_auto_schema(
        operation_description="Update course information",
        tags=['courses'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course_number': openapi.Schema(type=openapi.TYPE_STRING),
                'course_name': openapi.Schema(type=openapi.TYPE_STRING),
                'syllabus': openapi.Schema(type=openapi.TYPE_STRING),
                'semester': openapi.Schema(type=openapi.TYPE_STRING),
                'visible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'picture': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description='Course information',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'course_number': openapi.Schema(type=openapi.TYPE_STRING),
                        'course_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'syllabus': openapi.Schema(type=openapi.TYPE_STRING),
                        'semester': openapi.Schema(type=openapi.TYPE_STRING),
                        'visible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'picture': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def put(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        registration = get_object_or_404(
            Registration, user=user, course=course)

        if registration.userRole == Registration.UserRole.Student:
            content = {'message': 'Permission denied'}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        course_number = request.data.get('course_number').strip()
        course_name = request.data.get('course_name').strip()
        syllabus = request.data.get('syllabus').strip()
        semester = request.data.get('semester').strip()
        visible = request.data.get('visible')
        visible = True if visible == 'true' else False
        picture = request.data.get('picture')
        course.course_number = course_number
        course.course_name = course_name
        course.syllabus = syllabus
        course.semester = semester
        course.visible = visible
        course.picture = picture
        course.save()
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Delete course",
        tags=['courses'],
        responses={
            200: openapi.Response(
                description='Course information',
            ),
            403: openapi.Response(
                description='Permission denied',
            )
        }
    )
    def delete(self, request, course_id, *args, **kwargs):
        # delete course
        course = get_object_or_404(Course, pk=int(course_id))
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        registration = get_object_or_404(
            Registration, user=user, course=course)
        if registration.userRole == Registration.UserRole.Student:
            content = {'message': 'Permission denied'}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        try:
            course.delete()
        except Exception as error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_200_OK)


class CourseList(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]  # [IsAdminOrReadOnly]

    @swagger_auto_schema(
        operation_description="List all courses",
        tags=['courses'],
    )
    def get(self, request, *args, **kwargs):
        def get_registrations(user):
            registration = []
            for reg in Registration.objects.filter(user=user):
                if reg.course.visible == False:
                    continue
                else:
                    registration.append(reg)
            return registration

        def registrations_to_courses(registrations):
            courses = []
            for reg in registrations:
                course = Course.objects.get(id=reg.course.id)
                courses.append(course)
            return courses
        user = None
        # list courses
        if 'andrewId' in request.query_params:
            andrew_id = request.query_params['andrewId']
            user = CustomUser.objects.get(andrew_id=andrew_id)
        if user is None:
            registrations = Registration.objects.all()
            courses = registrations_to_courses(registrations)
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data)
        else:
            registrations = get_registrations(user)
            courses = registrations_to_courses(registrations)
            serializer = CourseSerializer(courses, many=True)
            data = []
            for (i, course) in enumerate(serializer.data):
                course['user_role'] = registrations[i].userRole
                course['points'] = registrations[i].points
                data.append(course)
            return Response(data)

    @swagger_auto_schema(
        operation_description="Create a new course",
        tags=['courses'],
    )
    def post(self, request, *args, **kwargs):
        # add course
        course_number = request.data.get('course_number')
        course_name = request.data.get('course_name').strip()
        syllabus = request.data.get('syllabus').strip()
        semester = request.data.get('semester').strip()
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        # boolean value visible
        visible = request.data.get('visible')
        visible = False if visible == 'false' else True
        picture = request.data.get('picture')
        course = Course.objects.create(
            course_number=course_number,
            course_name=course_name,
            syllabus=syllabus,
            semester=semester,
            visible=visible,
            picture=picture
        )
        course.save()
        registration = Registration(
            user=user, course=course, userRole=Registration.UserRole.Instructor)
        registration.save()
        serializer = CourseSerializer(course)
        return Response(serializer.data)
