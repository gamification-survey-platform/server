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
from app.gamification.models.xp_points import XpPoints
from app.gamification.serializers import UserSerializer

from django.conf import settings
import jwt
import os

from app.gamification.utils import get_user_pk


# class IsAdminUser(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.is_staff


class Users(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(id=user_id)
        if not user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = CustomUser.objects.all()
        serializer = UserSerializer(
            data, context={'request': request}, many=True)
        return Response(serializer.data)


class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, andrew_id, *args, **kwargs):
        try:
            data = CustomUser.objects.get(andrew_id=andrew_id)

            serializer = UserSerializer(data, context={'request': request})

            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, andrew_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(id=user_id)
        if not user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        modify_user = get_object_or_404(CustomUser, andrew_id=andrew_id)
        is_staff = request.data.get('is_staff')
        if is_staff is not None:
            modify_user.is_staff = True if is_staff == "true" else False
            modify_user.save()
        return Response(status=status.HTTP_200_OK)


class Login(generics.CreateAPIView):
    http_method_names = ['get', 'post']
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        andrew_id = request.data.get('andrew_id')
        password = request.data.get('password')
        user_data = None
        try:
            user = CustomUser.objects.get(andrew_id=andrew_id)
            serializer = UserSerializer(user, context={'request': request})
            user_data = serializer.data
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={ 'error': 'Failed to login. Username does not exist.' })
        try:
            xp_points = XpPoints.objects.get(user=user)
        except XpPoints.DoesNotExist:
            xp_points = XpPoints.objects.create(user=user)
            xp_points.save()
        user_data['exp_points'] = xp_points.exp_points
        user_data['exp'] = xp_points.exp
        user_data['level'] = xp_points.level
        if user.check_password(password):
            jwt_token = {'token': jwt.encode(
                {'id': user.id, 'is_staff': user.is_staff}, os.getenv('SECRET_KEY'), algorithm='HS256').decode('utf-8')}
            user_data['token'] = jwt_token['token']
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={ 'error': 'Failed to login. Invalid password.' })


class Register(generics.ListCreateAPIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        andrew_id = request.data.get('andrew_id')
        password = request.data.get('password')
        email = f'{andrew_id}@andrew.cmu.edu'
        try:
            user = CustomUser.objects.get(andrew_id=andrew_id)
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create(andrew_id=andrew_id, email=email)
            user.set_password(password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={ 'error': 'Failed to register. Username already taken.' })
