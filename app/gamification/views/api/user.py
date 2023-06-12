import os

import jwt
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models import CustomUser
from app.gamification.serializers import UserSerializer
from app.gamification.utils.levels import inv_level_func, level_func
from app.gamification.utils.s3 import generate_presigned_post, generate_presigned_url


class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def update_profile_picture(self, request, user):
        picture = request.FILES.get("image")
        if not picture:
            return None

        content_type = picture.content_type
        if content_type == "image/jpeg":
            file_ext = "jpg"
        elif content_type == "image/png":
            file_ext = "png"
        else:
            return None
        key = picture
        if settings.USE_S3:
            key = f"profile_pics/user_{user.id}.{file_ext}"
        user.image = key
        user.save()

        return key

    @swagger_auto_schema(operation_description="Get a user by user_id", tags=["users"])
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=user_id)
            response_data = self.get_serializer(user, context={"request": request}).data
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Generate the presigned URL to share with the user.
        if settings.USE_S3 and user.image is not None:
            download_url = generate_presigned_url(str(user.image), http_method="GET")
            response_data["image"] = download_url
        elif user.image is not None:
            download_url = f"http://{settings.ALLOWED_HOSTS[2]}:8000{user.image.url}"
            response_data["image"] = download_url

        return Response(response_data)

    @swagger_auto_schema(operation_description="Update a user by user_id", tags=["users"])
    def patch(self, request, user_id, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"message", "User not found."}, status=status.HTTP_404_NOT_FOUND)

        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")

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
        if settings.USE_S3 and key is not None:
            upload_url = generate_presigned_post(key)
            download_url = generate_presigned_url(key, http_method="GET")
            delete_url = generate_presigned_url(str(user.image), http_method="DELETE")
            response_data["upload_url"] = upload_url
            response_data["download_url"] = download_url
            response_data["delete_url"] = delete_url
        elif key is not None:
            upload_url = f"http://{settings.ALLOWED_HOSTS[2]}:8000{user.image.url}"
            download_url = f"http://{settings.ALLOWED_HOSTS[2]}:8000{user.image.url}"
            response_data["image"] = download_url

        return Response(response_data)


class Login(generics.CreateAPIView):
    http_method_names = ["get", "post"]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Login a user",
        tags=["login"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "andrew_id": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "andrew_id": "test",
                        "first_name": "test",
                        "last_name": "test",
                        "exp": 0,
                        "email": "test@andrew.cmu.edu",
                        "is_staff": True,
                        "is_active": True,
                        "is_superuser": True,
                        "date_joined": "2023-04-02T23:02:44.116000-07:00",
                        "level": 0,
                        "next_level_exp": 50,
                        "token": "<JWT>",
                    }
                },
            ),
            404: openapi.Response(
                description="Failed to login. Username does not exist.",
            ),
            400: openapi.Response(
                description="Failed to login. Password is incorrect.",
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        andrew_id = request.data.get("andrew_id")
        password = request.data.get("password")
        try:
            user = CustomUser.objects.get(andrew_id=andrew_id)
            serializer = UserSerializer(user, context={"request": request})
            response_data = serializer.data
        except CustomUser.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"message": "Failed to login. Username does not exist."}
            )
        response_data["exp"] = user.exp
        level = inv_level_func(user.exp)
        response_data["level"] = level
        response_data["next_level_exp"] = level_func(level + 1)
        # Generate the presigned URL to share with the user.
        if settings.USE_S3 and user.image:
            download_url = generate_presigned_url(str(user.image), http_method="GET")
            response_data["image"] = download_url
        elif user.image:
            download_url = f"http://{settings.ALLOWED_HOSTS[2]}:8000{user.image.url}"
            response_data["image"] = download_url

        if user.check_password(password):
            jwt_token = {
                "token": jwt.encode(
                    {"id": user.id, "is_staff": user.is_staff}, os.getenv("SECRET_KEY"), algorithm="HS256"
                ).decode("utf-8")
            }
            response_data["token"] = jwt_token["token"]
            response_data["message"] = "Vidya says hi"
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Failed to login. Invalid password."})


class Register(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Register a user",
        tags=["register"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "andrew_id": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(
                description="Register successful",
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        andrew_id = request.data.get("andrew_id")
        password = request.data.get("password")
        email = f"{andrew_id}@andrew.cmu.edu"
        try:
            user = CustomUser.objects.get(andrew_id=andrew_id)
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create(andrew_id=andrew_id, email=email)
            user.set_password(password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={"message": "Failed to register. Username already taken."}
        )
