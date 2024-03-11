from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models import Course, CustomUser, Registration
from app.gamification.serializers import CourseSerializer
from app.gamification.utils.auth import get_user_pk
from app.gamification.models.trivia import Trivia
from app.gamification.models.behavior import Behavior
from app.gamification.utils.levels import inv_level_func, level_func


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
        trivia_data = request.data.get("trivia")
        course = Course.objects.create(
            course_number=course_number,
            course_name=course_name,
            syllabus=syllabus,
            semester=semester,
            visible=visible,
            trivia_data=trivia_data,
        )
        trivia = None
        if trivia_data is not None and "question" in trivia_data and "answer" in trivia_data:
            trivia = Trivia(
                question=trivia_data["question"],
                answer=trivia_data["answer"],
                hints=trivia_data["hints"],
            )
        trivia.save()
        course.picture = picture
        course.save()
        registration = Registration(user=user, course=course)
        registration.save()
        serializer = CourseSerializer(course)
        return Response(serializer.data)

class CourseTrivia(generics.GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Submit trivia",
        tags=["course_trivia"],
    )
    def post(self, request, course_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        course = get_object_or_404(Course, id=course_id)
        registration = get_object_or_404(Registration, course=course, user=user)
        if not registration.trivia_completed:
            trivia = trivia
            answer = request.data.get("answer").strip().lower()
            if trivia.answer.strip().lower() == answer:
                behavior = Behavior.objects.get(operation="trivia")
                user.exp += behavior.points
                user.save()
                registration.points += behavior.points
                registration.course_experience += behavior.points
                registration.save()
                level = inv_level_func(user.exp)
                next_level_exp = level_func(level + 1)
                response_data = {
                    "message": f"Congrats! You gained {behavior.points} points!",
                    "exp": user.exp,
                    "level": level,
                    "next_level_exp": next_level_exp,
                    "points": registration.points,
                    "course_experience": registration.course_experience,
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Uh oh! Wrong answer."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Survey trivia already completed."}, status=status.HTTP_400_BAD_REQUEST)

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

        if course.trivia is not None:
            trivia_dict = model_to_dict(course.trivia)
            trivia_dict["completed"] = registration.trivia_completed

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
