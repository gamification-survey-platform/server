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
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class UserProfile(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description='Get user information by andrew id',
        tags=['profiles'],
        responses={
            200: openapi.Response(
                description='User profile',
                examples={
                    'application/json': {
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'email': '123@gmail.com'
                    }
                }
            )
        }
    )
    def create_profile_picture(self, request, user):
        picture = request.FILES.get('image')
        if not picture:
            return None

        content_type = picture.content_type
        if content_type == 'image/jpeg':
            file_ext = 'jpg'
        elif content_type == 'image/png':
            file_ext = 'png'
        else:
            return None

        if settings.USE_S3:
            key = f'users/user_{user.id}.{file_ext}'
        else:
            key = picture

        return key

    def get(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(id=user_id)
        user_info = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'image': user.image
        }
        return Response(user_info)

    @swagger_auto_schema(
        operation_description='Update user information by andrew id',
        tags=['profiles'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )

    )
    def patch(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(id=user_id)
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        image = request.data.get('image')
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        if image:
            image_key = self.create_profile_picture(request, user)
            user.image = image_key
        user.save()
        user_info = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        if user.image:
            user_info['image'] = user.image
        return Response(user_info)
