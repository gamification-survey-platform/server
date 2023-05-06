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
import jwt
import os

from app.gamification.utils import get_user_pk, level_func, inv_level_func

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


# class IsAdminUser(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.is_staff


class Users(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description='List all users in the system',
        tags=['users']
    )
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

    @swagger_auto_schema(
        operation_description='Get a user by andrew id',
        tags=['users']
    )
    def get(self, request, andrew_id, *args, **kwargs):
        try:
            data = CustomUser.objects.get(andrew_id=andrew_id)

            serializer = UserSerializer(data, context={'request': request})

            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description='Update a user is_staff field by andrew id',
        tags=['users']
    )
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

    @swagger_auto_schema(
        operation_description='Login a user',
        tags=['users'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'andrew_id': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description='Login successful',
                examples={
                    'application/json': {
                        'id': 1,
                        'andrew_id': 'test',
                        'first_name': 'test',
                        'last_name': 'test',
                        'email': '123@gmail.com',
                        'is_staff': False,
                        'exp': 0,
                        'level': 1,
                        'next_level_exp': 100
                    }
                }
            ),
            404: openapi.Response(
                description='Failed to login. Username does not exist.',
            ),

            400: openapi.Response(
                description='Failed to login. Password is incorrect.',
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        andrew_id = request.data.get('andrew_id')
        password = request.data.get('password')
        user_data = None
        try:
            user = CustomUser.objects.get(andrew_id=andrew_id)
            serializer = UserSerializer(user, context={'request': request})
            user_data = serializer.data
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Failed to login. Username does not exist.'})
        user_data['exp'] = user.exp
        level = inv_level_func(user.exp)
        user_data['level'] = level
        user_data['next_level_exp'] = level_func(level + 1)
        if user.check_password(password):
            jwt_token = {'token': jwt.encode(
                {'id': user.id, 'is_staff': user.is_staff}, os.getenv('SECRET_KEY'), algorithm='HS256').decode('utf-8')}
            user_data['token'] = jwt_token['token']
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Failed to login. Invalid password.'})


class Register(generics.ListCreateAPIView):

    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description='Register a user',
        tags=['users'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={

                'andrew_id': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description='Register successful',
            ),
        }
    )
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
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Failed to register. Username already taken.'})
