from rest_framework.views import APIView
from rest_framework.response import Response
from app.gamification.models import Trivia, UserTrivia
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from app.gamification.serializers.trivia import TriviaSerializer
from rest_framework import generics
from rest_framework.response import Response
from app.gamification.models import Trivia, UserTrivia
from app.gamification.models.user import CustomUser
from app.gamification.utils.auth import get_user_pk
from app.gamification.utils.levels import inv_level_func, level_func
from app.gamification.models.registration import Registration
from app.gamification.models.behavior import Behavior


class MarkTriviaCompletedView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    triviaserializer_class = TriviaSerializer
    def post(self, request, trivia_id):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        trivia = get_object_or_404(Trivia, pk=trivia_id)
        user_trivia, created = UserTrivia.objects.get_or_create(user=user, trivia=trivia, is_completed=False)
        if not created:
            return Response({'message': 'Trivia already completed'}, status=status.HTTP_208_ALREADY_REPORTED)
        user_trivia.is_completed = True
        user_trivia.save()

        hints_used = request.data.get('hintsUsed', 0)
        initial_points = 12
        for i in range(hints_used):
            initial_points = max(0, initial_points // 2)
        points = initial_points
        # Update user points and experience
        registration = Registration.objects.get(user=user, course=trivia.course)
        user.exp += points
        user.save()
        registration.points += points
        registration.course_experience += points
        registration.save()
        level = inv_level_func(user.exp)
        next_level_exp = level_func(level + 1)

        response_data = {
            "message": f"Congrats! You gained {points} points!",
            "exp": user.exp,
            "level": level,
            "next_level_exp": next_level_exp,
            "points": registration.points,
            "course_experience": registration.course_experience,
        }
        return Response(response_data, status=status.HTTP_200_OK)
