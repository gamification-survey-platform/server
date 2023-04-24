from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from app.gamification.utils import level_func
from app.gamification.serializers.xp_points import XpPointsSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class LevelList(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = XpPointsSerializer

    @swagger_auto_schema(
        operation_description='List all levels in the system',
        tags=['levels']
    )
    def get(self, request, level, *args, **kwargs):
        exp = level_func(int(level))
        return Response({'exp': exp})
