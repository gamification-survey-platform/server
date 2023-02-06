from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from app.gamification.models import Course, Registration
from app.gamification.serializers import CourseSerializer
from django.shortcuts import get_object_or_404, redirect, render

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


class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self, request, *args, **kwargs):
        # list courses
        if request.user.is_staff:
            queryset = Course.objects.all()
        else:
            queryset = Course.objects.filter(visible=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    lookup_field = 'id'
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAdminUser]


class ViewACourse(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
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


# @login_required
# @user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA])
# def edit_course(request, course_id):
#     course = get_object_or_404(Course, pk=course_id)
#     if request.method == 'POST':
#         form = CourseForm(request.POST, request.FILES,
#                           instance=course, label_suffix='')

#         if form.is_valid():
#             course = form.save()
#         return redirect('course')

#     else:
#         form = CourseForm(instance=course)
#         return render(request, 'edit_course.html', {'course': course, 'form': form})
class EditACourse(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, course_id, *args, **kwargs):
        # edit course details
        course = get_object_or_404(Course, pk=course_id)
        registration = get_object_or_404(
            Registration, users=request.user, courses=course)

        if registration.userRole == Registration.UserRole.Student:
            # return 403 and error message
            content = {'message': 'Permission denied'}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(course, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
class DeleteACourse(generics.DestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

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
        