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
import jwt
import os


# class IsAdminUser(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.is_staff


class Users(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        data = CustomUser.objects.all()
        serializer = UserSerializer(
            data, context={'request': request}, many=True)
        return Response(serializer.data)


class UserDetail(generics.RetrieveAPIView):
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
            return Response(status=status.HTTP_404_NOT_FOUND)
        if user.check_password(password):
            jwt_token = {'token': jwt.encode(
                {'id': user.id, 'is_staff': user.is_staff}, os.getenv('SECRET_KEY'), algorithm='HS256').decode('utf-8')}
            user_data['token'] = jwt_token['token']
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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

        return Response(status=status.HTTP_400_BAD_REQUEST)
