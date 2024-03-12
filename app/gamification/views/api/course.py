import json
from django.shortcuts import get_object_or_404
from app.gamification.models.trivia import Trivia
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models import Course, CustomUser, Registration
from app.gamification.serializers import CourseSerializer
from app.gamification.utils.auth import get_user_pk


class CourseList(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="List of all a user's courses",
        tags=["courses"],
        responses={
            200: openapi.Response(
                description="Each course information along with relevant registration information",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "course_number": openapi.Schema(type=openapi.TYPE_STRING),
                            "course_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "syllabus": openapi.Schema(type=openapi.TYPE_STRING),
                            "semester": openapi.Schema(type=openapi.TYPE_STRING),
                            "visible": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "picture": openapi.Schema(type=openapi.TYPE_STRING),
                            "user_role": openapi.Schema(type=openapi.TYPE_STRING, enum=["Student", "TA", "Instructor"]),
                            "points": openapi.Schema(type=openapi.TYPE_INTEGER),
                        },
                    ),
                ),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        registrations = Registration.objects.filter(user=user)
        courses = []
        for reg in registrations:
            course = Course.objects.get(id=reg.course.id)
            courses.append(course)
        serializer = CourseSerializer(courses, many=True)
        response_data = []
        for i, course in enumerate(serializer.data):
            course["is_staff"] = registrations[i].user.is_staff
            course["points"] = registrations[i].points
            response_data.append(course)
        return Response(response_data)

    @swagger_auto_schema(
        operation_description="Create a new course",
        tags=["courses"],
    )
    def post(self, request, *args, **kwargs):
        # add course
        course_number = request.data.get("course_number")
        course_name = request.data.get("course_name").strip()
        syllabus = request.data.get("syllabus").strip()
        semester = request.data.get("semester").strip()
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        visible = request.data.get("visible")
        visible = False if visible == "false" else True
        picture = request.data.get("picture")

        # Check if trivia is set
        is_trivia_enabled = request.data.get("enableTrivia") == 'true'

        course = Course.objects.create(
            course_number=course_number,
            course_name=course_name,
            syllabus=syllabus,
            semester=semester,
            visible=visible
        )
        course.picture = picture
        course.save()

        # Get trivia data
        if is_trivia_enabled:
            question = request.data.get("question")
            answer = request.data.get("answer")
            hints = []
            for key in request.data.keys():
                if key.startswith("hint"):
                    hints.append(request.data.get(key))
            if question and answer:
                trivia = Trivia(
                    course=course,
                    question=question,
                    answer=answer,
                    hints=hints
                )
            trivia.save()

        registration = Registration(user=user, course=course)
        registration.save()
        serializer = CourseSerializer(course)
        return Response(serializer.data)


class CourseTeamList(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="List of all the teams in a course",
        tags=["courses-team"],
        responses={
            200: openapi.Response(
                description="Each course information along with relevant registration information",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "course_number": openapi.Schema(type=openapi.TYPE_STRING),
                            "course_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "syllabus": openapi.Schema(type=openapi.TYPE_STRING),
                            "semester": openapi.Schema(type=openapi.TYPE_STRING),
                            "visible": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "picture": openapi.Schema(type=openapi.TYPE_STRING),
                            "user_role": openapi.Schema(type=openapi.TYPE_STRING, enum=["Student", "TA", "Instructor"]),
                            "points": openapi.Schema(type=openapi.TYPE_INTEGER),
                        },
                    ),
                ),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        registrations = Registration.objects.filter(user=user)
        courses = []
        for reg in registrations:
            course = Course.objects.get(id=reg.course.id)
            courses.append(course)
        serializer = CourseSerializer(courses, many=True)
        response_data = []
        for i, course in enumerate(serializer.data):
            course["is_staff"] = registrations[i].user.is_staff
            course["points"] = registrations[i].points
            response_data.append(course)
        return Response(response_data)

    @swagger_auto_schema(
        operation_description="Create a new course",
        tags=["courses"],
    )
    def post(self, request, *args, **kwargs):
        # add course
        course_number = request.data.get("course_number")
        course_name = request.data.get("course_name").strip()
        syllabus = request.data.get("syllabus").strip()
        semester = request.data.get("semester").strip()
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        visible = request.data.get("visible")
        visible = False if visible == "false" else True
        picture = request.data.get("picture")
        course = Course.objects.create(
            course_number=course_number,
            course_name=course_name,
            syllabus=syllabus,
            semester=semester,
            visible=visible,
        )
        course.picture = picture
        course.save()
        registration = Registration(user=user, course=course)
        registration.save()
        serializer = CourseSerializer(course)
        return Response(serializer.data)


class CourseDetail(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get course information",
        tags=["courses"],
        responses={
            200: openapi.Response(
                description="Course information",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "course_number": openapi.Schema(type=openapi.TYPE_STRING),
                        "course_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "syllabus": openapi.Schema(type=openapi.TYPE_STRING),
                        "semester": openapi.Schema(type=openapi.TYPE_STRING),
                        "visible": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "picture": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            )
        },
    )
    def get(self, request, course_id, *args, **kwargs):
        andrew_id = get_user_pk(request)
        user = CustomUser.objects.get(andrew_id=andrew_id)
        course = get_object_or_404(Course, pk=course_id)
        registration = get_object_or_404(Registration, user=user, course=course)
        if course.visible is False and not user.is_staff:
            return Response({"message": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        serializer = CourseSerializer(course)
        response_data = serializer.data
        response_data["points"] = registration.points
        response_data["course_experience"] = registration.course_experience
        response_data["is_staff"] = user.is_staff

        return Response(response_data)

    @swagger_auto_schema(
        operation_description="Update course information",
        tags=["courses"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "course_number": openapi.Schema(type=openapi.TYPE_STRING),
                "course_name": openapi.Schema(type=openapi.TYPE_STRING),
                "syllabus": openapi.Schema(type=openapi.TYPE_STRING),
                "semester": openapi.Schema(type=openapi.TYPE_STRING),
                "visible": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "picture": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(
                description="Course information",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "course_number": openapi.Schema(type=openapi.TYPE_STRING),
                        "course_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "syllabus": openapi.Schema(type=openapi.TYPE_STRING),
                        "semester": openapi.Schema(type=openapi.TYPE_STRING),
                        "visible": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "picture": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            )
        },
    )
    def put(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        if not user.is_staff:
            return Response({"message": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        course_number = request.data.get("course_number").strip()
        course_name = request.data.get("course_name").strip()
        syllabus = request.data.get("syllabus").strip()
        semester = request.data.get("semester").strip()
        visible = request.data.get("visible")
        visible = True if visible == "true" else False
        picture = request.data.get("picture")
        # Check if trivia is set
        is_trivia_enabled = request.data.get("enableTrivia") == 'true'
        # Get trivia data
        if is_trivia_enabled:
            question = request.data.get("question")
            answer = request.data.get("answer")
            hints = []
            for key in request.data.keys():
                if key.startswith("hint"):
                    hints.append(request.data.get(key))
            if question and answer:
                trivia = Trivia(
                    course=course,
                    question=question,
                    answer=answer,
                    hints=hints
                )
            trivia.save()
        elif course.trivia is not None:
            course.trivia.delete()

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
        tags=["courses"],
        responses={
            200: openapi.Response(
                description="Course information",
            ),
            403: openapi.Response(
                description="Permission denied",
            ),
        },
    )
    def delete(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        if not user.is_staff:
            return Response({"message": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        try:
            course.delete()
        except Exception:
            return Response(
                {"message": "Cannot delete course. Another user is likely registered for the course."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(status=status.HTTP_200_OK)
