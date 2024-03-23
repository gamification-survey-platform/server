from datetime import datetime, timedelta
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from app.gamification.models.behavior import Behavior
from app.gamification.models.course import Course
from app.gamification.models.registration import Registration
from app.gamification.models.user import CustomUser
from app.gamification.models.trivia import Trivia
from app.gamification.serializers.trivia import TriviaSerializer
from app.gamification.utils.auth import get_user_pk
from app.gamification.utils.levels import inv_level_func, level_func


class TriviaView(generics.GenericAPIView):
    serializer_class = TriviaSerializer
    permission_classes = [AllowAny]
    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        trivia_qs = Trivia.objects.filter(course=course)
        if trivia_qs.exists():
            serializer = TriviaSerializer(trivia_qs, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)