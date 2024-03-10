from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models import Course, CustomUser, Trivia
from app.gamification.utils.auth import get_user_pk
from app.gamification.serializers import CourseSerializer
from datetime import datetime, timedelta

import pandas as pd
import pytz
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from app.gamification.models.assignment import Assignment
from app.gamification.models.behavior import Behavior
from app.gamification.models.course import Course
from app.gamification.models.registration import Registration
from app.gamification.models.user import CustomUser
from app.gamification.utils.auth import get_user_pk
from app.gamification.utils.levels import inv_level_func, level_func
import logging
logger = logging.getLogger(__name__)


class CourseTrivia(generics.GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Submit course trivia",
        tags=["course"],
    )
    def post(self, request, course_id, *args, **kwargs):
        logger.debug("Trivia submission for course_id %s: %s", course_id, request.data)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        course = get_object_or_404(Course, id=course_id)
        registration = Registration.objects.get(user=user, course=course)
        trivia = course.trivia
        answer = request.data.get("answer").strip().lower()
        if trivia.answer.strip().lower() == answer:
            logger.debug("Correct answer for course_id %s", course_id)
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
            logger.debug("Wrong answer for course_id %s", course_id)
            return Response({"message": "Uh oh! Wrong answer."}, status=status.HTTP_400_BAD_REQUEST)
