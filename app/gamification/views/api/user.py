from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import permissions
import json

from app.gamification.models import CustomUser
from app.gamification.serializers import UserSerializer

from rest_framework.response import Response
from rest_framework import status


from app.gamification.models import CustomUser
from app.gamification.serializers import UserSerializer

from django.conf import settings
import jwt
import os
from app.gamification.utils.s3 import generate_presigned_post, generate_presigned_url
from app.gamification.utils.auth import get_user_pk
from app.gamification.utils.levels import level_func, inv_level_func

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Get a user by user_id',
        tags=['users']
    )
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=user_id)
            response_data = self.get_serializer(user, context={'request': request}).data
        except CustomUser.DoesNotExist:
            return Response({ 'message': 'User not found' }, status=status.HTTP_404_NOT_FOUND)

        # Generate the presigned URL to share with the user.
        if settings.USE_S3 and user.image != None:
            upload_url = generate_presigned_post(user.image)
            download_url = generate_presigned_url(user.image, http_method='GET')
            response_data['image'] = download_url
        elif user.image != None:
            upload_url = f'http://{settings.ALLOWED_HOSTS[1]}:8000{user.image.url}'
            download_url = f'http://{settings.ALLOWED_HOSTS[1]}:8000{user.image.url}'
            response_data['image'] = download_url

        return Response(response_data)

    @swagger_auto_schema(
        operation_description='Update a user by user_id',
        tags=['users']
    )
    def patch(self, request, user_id, *args, **kwargs):
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
        
        response_data = self.get_serializer(user).data

        key = self.update_profile_picture(request, user)

        # Generate the presigned URL to share with the user.
        if settings.USE_S3 and key != None:
            upload_url = generate_presigned_post(key)
            download_url = generate_presigned_url(key, http_method='GET')
            delete_url = generate_presigned_url(
                    str(user.image), http_method='DELETE')
            response_data['upload_url'] = upload_url
            response_data['download_url'] = download_url
            response_data['delete_url'] = delete_url
        elif key != None:
            upload_url = f'http://{settings.ALLOWED_HOSTS[1]}:8000{user.image.url}'
            download_url = f'http://{settings.ALLOWED_HOSTS[1]}:8000{user.image.url}'
            response_data['image'] = download_url

        return Response(response_data)

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
