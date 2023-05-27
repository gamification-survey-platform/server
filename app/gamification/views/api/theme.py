from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.response import Response

from app.gamification.models import CustomUser, Theme
from app.gamification.utils.auth import get_user_pk


class ThemeDetail(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get user theme",
        tags=["theme"],
        responses={
            200: openapi.Schema(
                description="Get color theme for user",
                type=openapi.TYPE_OBJECT,
                properties={
                    "colorBgBase": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorTextBase": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorPrimary": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorSuccess": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorWarning": openapi.Schema(type=openapi.TYPE_STRING),
                    "colorError": openapi.Schema(type=openapi.TYPE_STRING),
                    "cursor": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        if user.theme:
            response_data = model_to_dict(user.theme)
        else:
            response_data = {}
        return Response(response_data)

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
        for key in request.data:
            setattr(theme, key, request.data[key])
        theme.save()
        user.theme = theme
        user.save()
        response_data = model_to_dict(theme)
        return Response(response_data)
