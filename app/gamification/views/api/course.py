from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from app.gamification.models import Course, Registration, CustomUser
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
        def get_registrations(user):
            registration = []
            for reg in Registration.objects.filter(users=user):
                if reg.userRole == Registration.UserRole.Student and reg.courses.visible == False:
                    continue
                else:
                    registration.append(reg)
            return registration
        # list courses
        andrew_id = request.data.andrewId
        user = CustomUser.objects.get(andrewId=andrew_id)
        if user.is_staff:
            registrations = Registration.objects.all()
        else:
            registrations = get_registrations(user)
        serializer = RegistrationSerializer(registrations)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # add course
        course_number = request.data.get('course_number').strip()
        course_name = request.data.get('course_name').strip()
        syllabus =  request.data.get('syllabus').strip()
        semester = request.data.get('semester').strip()
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
            users=request.user, courses=course, userRole=Registration.UserRole.Instructor)
        registration.save()
        serializer = CourseSerializer(course)
        return Response(serializer.data)


# class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Course.objects.all()
#     lookup_field = 'id'
#     serializer_class = CourseSerializer
#     permission_classes = [permissions.IsAdminUser]


class ManageACourse(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny] # [permissions.IsAuthenticated]
    
    def get(self, request, course_id, *args, **kwargs):
        # view course details
        course = get_object_or_404(Course, pk=course_id)
        registration = get_object_or_404(
            Registration, users=request.user, courses=course)

        if course.visible == False and registration.userRole == Registration.UserRole.Student:
            # return 403 and error message
            content = {'message': 'Permission denied'}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        serializer = CourseSerializer(course)
        # serializer = self.get_serializer(course)
        return Response(serializer.data)


    def delete(self, request, course_id, *args, **kwargs):
        # delete course
        course = get_object_or_404(Course, pk=course_id)
        registration = get_object_or_404(
            Registration, users=request.user, courses=course)

        if registration.userRole == Registration.UserRole.Student:
            # return 403 and error message
            content = {'message': 'Permission denied'}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        course.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT
        return Response(status=status.HTTP_200_OK)

    def put(self, request, course_id, *args, **kwargs):
        # edit course details
        course = get_object_or_404(Course, pk=course_id)
        registration = get_object_or_404(
            Registration, users=request.user, courses=course)

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
