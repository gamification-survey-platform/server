from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import permissions
import json
from app.gamification.models import CustomUser
from app.gamification.serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.gamification.models import CustomUser
from app.gamification.serializers import UserSerializer
from django.conf import settings
from app.gamification.utils import get_user_pk


class UserProfile(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(id=user_id)
        user_info = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }
        return Response(user_info)

    def patch(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(id=user_id)
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        user.save()
        user_info = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }
        return Response(user_info)
