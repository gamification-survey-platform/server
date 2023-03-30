from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from app.gamification.models import Course, Registration, CustomUser
from app.gamification.utils import get_user_pk
from app.gamification.serializers import CourseSerializer, RegistrationSerializer
from django.shortcuts import get_object_or_404

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


class CourseList(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes =  [permissions.AllowAny] # [IsAdminOrReadOnly]
    
    def get(self, request, *args, **kwargs):
        if 'course_id' in request.query_params:
            course_id = request.query_params['course_id']
            # view course details
            andrew_id = get_user_pk(request)
            user = CustomUser.objects.get(andrew_id=andrew_id)
            course = get_object_or_404(Course, pk=course_id)
            registration = get_object_or_404(
                Registration, users=user, courses=course)

            if course.visible == False and registration.userRole == Registration.UserRole.Student:
                # return 403 and error message
                content = {'message': 'Permission denied'}
                return Response(content, status=status.HTTP_403_FORBIDDEN)
            serializer = CourseSerializer(course)
            # serializer = self.get_serializer(course)
            return Response(serializer.data)
        else:
            def get_registrations(user):
                registration = []
                for reg in Registration.objects.filter(users=user):
                    if reg.courses.visible == False:
                        continue
                    else:
                        registration.append(reg)
                return registration
            def registrations_to_courses(registrations):
                courses = []
                for reg in registrations:
                    course = Course.objects.get(id=reg.courses.id)
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
                    data.append(course)
                return Response(data)

    def post(self, request, *args, **kwargs):
        # add course
        course_number = request.data.get('course_number').strip()
        course_name = request.data.get('course_name').strip()
        syllabus =  request.data.get('syllabus').strip()
        semester = request.data.get('semester').strip()
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        # boolean value visible
        visible = request.data.get('visible')
        visible = True if visible == 'true' else False
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
            users=user, courses=course, userRole=Registration.UserRole.Instructor)
        registration.save()
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        if 'course_id' in request.query_params:
            # delete course
            course_id = request.query_params['course_id']
            course = get_object_or_404(Course, pk=int(course_id))
            user_pk = get_user_pk(request)
            user = CustomUser.objects.get(pk=user_pk)
            if not user.is_staff:
                registration = get_object_or_404(
                    Registration, users=user, courses=course)
                if registration.userRole == Registration.UserRole.Student:
                    # return 403 and error message
                    content = {'message': 'Permission denied'}
                    return Response(content, status=status.HTTP_403_FORBIDDEN)
            course.delete()
            # return Response(status=status.HTTP_204_NO_CONTENT
            return Response(status=status.HTTP_200_OK)
        else:
            # missing data, return 400 and error message
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        if 'course_id' in request.query_params:
            course_id = request.query_params['course_id']
            # edit course details
            course = get_object_or_404(Course, pk=course_id)
            user_pk = get_user_pk(request)
            user = CustomUser.objects.get(pk=user_pk)
            registration = get_object_or_404(
                Registration, users=user, courses=course)

            if registration.userRole == Registration.UserRole.Student:
                # return 403 and error message
                content = {'message': 'Permission denied'}
                return Response(content, status=status.HTTP_403_FORBIDDEN)
            course_number = request.data.get('course_number').strip()
            course_name = request.data.get('course_name').strip()
            syllabus =  request.data.get('syllabus').strip()
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
        else:
            # missing data, return 400 and error message
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
