from datetime import datetime, timedelta
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models.behavior import Behavior
from app.gamification.models.course import Course
from app.gamification.models.registration import Registration
from app.gamification.models.user import CustomUser
from app.gamification.models.trivia import Trivia
from app.gamification.serializers.trivia import TriviaSerializer
from app.gamification.utils.auth import get_user_pk
from app.gamification.utils.levels import inv_level_func, level_func

class Trivia(generics.GenericAPIView):
    queryset = Trivia.objects.all()
    serializer_class = TriviaSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        trivia = get_object_or_404(Trivia, course=course)
        serializer = TriviaSerializer(trivia)
        return Response(serializer.data)
    

    def post(self, request, course_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        trivia = get_object_or_404(Trivia, course=course)
        course = get_object_or_404(Course, id=course_id)
        registration = get_object_or_404(Registration, course=course, user=user)
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