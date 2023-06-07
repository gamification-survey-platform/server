from datetime import datetime

import pytz
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models import (
    Assignment,
    Course,
    CustomUser,
    Registration,
    UserRole,
)
from app.gamification.serializers import AssignmentSerializer
from app.gamification.utils.auth import get_user_pk


class AssignmentList(generics.ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get all assignments information",
        tags=["assignments"],
        responses={
            200: openapi.Response(
                description="Each assignment details with user role",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "course": openapi.Schema(type=openapi.TYPE_INTEGER, description="course id"),
                            "assignment_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                            "assignment_type": openapi.Schema(type=openapi.TYPE_STRING, enum=["Individual", "Team"]),
                            "submission_type": openapi.Schema(type=openapi.TYPE_STRING, enum=["File", "URL", "Text"]),
                            "total_score": openapi.Schema(type=openapi.TYPE_NUMBER),
                            "weight": openapi.Schema(type=openapi.TYPE_NUMBER),
                            "date_released": openapi.Schema(type=openapi.TYPE_STRING),
                            "date_due": openapi.Schema(type=openapi.TYPE_STRING),
                            "user_role": openapi.Schema(type=openapi.TYPE_STRING, enum=["Student", "TA", "Instructor"]),
                        },
                    ),
                ),
            )
        },
    )
    def get(self, request, course_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        user_role = Registration.objects.get(user=user, course=course_id).userRole
        course = get_object_or_404(Course, pk=course_id)
        assignments = Assignment.objects.filter(course=course)
        assignments = [model_to_dict(assignment) for assignment in assignments]
        response_data = []
        for assignment in assignments:
            if (
                datetime.now().astimezone(pytz.timezone("America/Los_Angeles")) > assignment["date_released"]
                or user_role != UserRole.Student
            ):
                assignment["user_role"] = user_role
                response_data.append(assignment)
        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new assignment",
        tags=["assignments"],
    )
    def post(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        userRole = Registration.objects.get(user=user, course=course).userRole
        assignment_name = request.data.get("assignment_name")
        assignment_type = request.data.get("assignment_type")
        date_released = request.data.get("date_released")
        date_due = request.data.get("date_due")
        description = request.data.get("description")
        submission_type = request.data.get("submission_type")
        total_score = request.data.get("total_score")
        weight = request.data.get("weight")
        review_assign_policy = request.data.get("review_assign_policy")
        if userRole == UserRole.Instructor:
            assignment = Assignment.objects.create(
                course=course,
                assignment_name=assignment_name,
                assignment_type=assignment_type,
                date_released=date_released,
                date_due=date_due,
                description=description,
                submission_type=submission_type,
                total_score=total_score,
                weight=weight,
                review_assign_policy=review_assign_policy,
            )
            assignment.save()
            data = model_to_dict(assignment)
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class AssignmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get assignment information",
        tags=["assignments"],
        responses={
            200: openapi.Schema(
                description="Assignment details with user role",
                type=openapi.TYPE_OBJECT,
                properties={
                    "pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "course": openapi.Schema(type=openapi.TYPE_INTEGER, description="course id"),
                    "assignment_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                    "assignment_type": openapi.Schema(type=openapi.TYPE_STRING, enum=["Individual", "Team"]),
                    "submission_type": openapi.Schema(type=openapi.TYPE_STRING, enum=["File", "URL", "Text"]),
                    "total_score": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "weight": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "date_released": openapi.Schema(type=openapi.TYPE_STRING),
                    "date_due": openapi.Schema(type=openapi.TYPE_STRING),
                    "user_role": openapi.Schema(type=openapi.TYPE_STRING, enum=["Student", "TA", "Instructor"]),
                },
            )
        },
    )
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        userRole = Registration.objects.get(user=user, course=course).userRole
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        data = model_to_dict(assignment)
        data["user_role"] = userRole
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="update an assignment",
        tags=["assignments"],
    )
    def patch(self, request, course_id, assignment_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        userRole = Registration.objects.get(user=user, course=course).userRole
        assignment_name = request.data.get("assignment_name")
        assignment_type = request.data.get("assignment_type")
        date_due = request.data.get("date_due")
        date_released = request.data.get("date_released")
        description = request.data.get("description")
        submission_type = request.data.get("submission_type")
        total_score = request.data.get("total_score")
        weight = request.data.get("weight")
        review_assign_policy = request.data.get("review_assign_policy")
        if userRole == UserRole.Instructor:
            try:
                assignment = Assignment.objects.get(pk=assignment_id)
            except Assignment.DoesNotExist:
                assignment = Assignment()
            assignment.course = course
            assignment.assignment_name = assignment_name
            assignment.assignment_type = assignment_type
            assignment.date_due = date_due
            assignment.date_released = date_released
            assignment.description = description
            assignment.submission_type = submission_type
            assignment.total_score = total_score
            assignment.weight = weight
            assignment.review_assign_policy = review_assign_policy
            assignment.save()
            data = model_to_dict(assignment)
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description="Delete an assignment",
        tags=["assignments"],
    )
    def delete(self, request, course_id, assignment_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        if user.is_staff or Registration.objects.get(user=user, course=course).userRole == UserRole.Instructor:
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            assignment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
