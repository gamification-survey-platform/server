from django.conf import settings
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.response import Response

from app.gamification.models import CustomUser, Theme
from app.gamification.utils.auth import get_user_pk
from app.gamification.utils.s3 import generate_presigned_post, generate_presigned_url

image_fields = [
    "cursor",
    "multiple_choice_item",
    "multiple_select_item",
    "scale_multiple_choice_item",
    "multiple_choice_target",
    "multiple_select_target",
    "scale_multiple_choice_target",
]


class ThemeDetail(generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]

    def update_theme_icon(self, request, user, theme, icon_type):
        icon = request.FILES.get(icon_type)
        if not icon:
            setattr(theme, icon_type, None)
            theme.save()
            return None

        content_type = icon.content_type
        if content_type == "image/jpeg" or content_type == "image/jpg":
            file_ext = "jpg"
        elif content_type == "image/png":
            file_ext = "png"
        else:
            return None
        key = icon
        if settings.USE_S3:
            key = f"{icon_type}/{icon_type}_{user.id}.{file_ext}"
        setattr(theme, icon_type, key)
        theme.save()

        return key

    @swagger_auto_schema(
        operation_description="Get user theme",
        tags=["theme"],
        responses={
            200: openapi.Schema(
                description="Get theme for user",
                type=openapi.TYPE_OBJECT,
                properties={
                    "colorBgBase": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorTextBase": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorPrimary": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorSuccess": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorWarning": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorError": openapi.Schema(type=openapi.TYPE_STRING),
                    "cursor": openapi.Schema(type=openapi.TYPE_STRING),
                    "multiple_choice_icon": openapi.Schema(type=openapi.TYPE_STRING),
                    "multiple_select_icon": openapi.Schema(type=openapi.TYPE_STRING),
                    "scale_multiple_choice_icon": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        if user.theme:
            response_data = model_to_dict(user.theme, exclude=image_fields)
            for image in image_fields:
                key = getattr(user.theme, image)
                if key:
                    download_url = generate_presigned_url(str(key), http_method="GET")
                    response_data[image] = download_url
        else:
            response_data = {}
        return Response(response_data)

    @swagger_auto_schema(
        operation_description="Create user theme",
        tags=["theme"],
        responses={
            200: openapi.Schema(
                description="Create theme",
                type=openapi.TYPE_OBJECT,
                properties={
                    "colorBgBase": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorTextBase": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorPrimary": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorSuccess": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorWarning": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorError": openapi.Schema(type=openapi.TYPE_STRING),
                    "cursor": openapi.Schema(type=openapi.TYPE_STRING),
                    "multiple_choice_icon": openapi.Schema(type=openapi.TYPE_STRING),
                    "multiple_select_icon": openapi.Schema(type=openapi.TYPE_STRING),
                    "scale_multiple_choice_icon": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        # user_id = get_user_pk(request)
        # user = get_object_or_404(CustomUser, id=user_id)

        return Response()

    @swagger_auto_schema(
        operation_description="Edit user theme",
        tags=["theme"],
        responses={
            200: openapi.Schema(
                description="Edit color theme for user, returns new theme",
                type=openapi.TYPE_OBJECT,
                properties={
                    "colorBgBase": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorTextBase": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorPrimary": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorSuccess": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorWarning": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorError": openapi.Schema(type=openapi.TYPE_STRING),
                    "cursor": openapi.Schema(type=openapi.TYPE_STRING),
                    "multiple_choice_icon": openapi.Schema(type=openapi.TYPE_STRING),
                    "multiple_select_icon": openapi.Schema(type=openapi.TYPE_STRING),
                    "scale_multiple_choice_icon": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        },
    )
    def patch(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        if user.theme:
            theme = user.theme
        else:
            theme = Theme()
            theme.creator = user
        response_data = {}
        field = list(request.data.keys())[0]
        if field in image_fields:
            upload_url = None
            download_url = None
            delete_url = None
            if str(getattr(theme, field)):
                delete_url = generate_presigned_url(str(getattr(theme, field)), http_method="DELETE")

            key = self.update_theme_icon(request, user, theme, field)
            if key:
                upload_url = generate_presigned_post(key)
                download_url = generate_presigned_url(key, http_method="GET")
            response_data["upload_url"] = upload_url
            response_data["download_url"] = download_url
            response_data["delete_url"] = delete_url
        else:
            for key in request.data:
                setattr(theme, key, request.data[key])
            theme.save()
            response_data = model_to_dict(theme, exclude=image_fields)

        user.theme = theme
        user.save()

        return Response(response_data)
