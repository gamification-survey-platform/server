from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from app.gamification.utils import level_func

class LevelList(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, level, *args, **kwargs):
        exp = level_func(int(level))
        return Response({ 'exp': exp })
