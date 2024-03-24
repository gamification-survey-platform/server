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
        return Response({'message': 'Trivia marked as completed'}, status=status.HTTP_200_OK)
