from app.gamification.models.xp_points import XpPoints
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from app.gamification.models.user import CustomUser
from app.gamification.models.behavior import Behavior
from app.gamification.models.exp_history import ExpHistory
from app.gamification.utils import get_user_pk, ASSIGNMENT_POINTS, SURVEY_POINTS, level_func
from app.gamification.serializers.xp_points import XpPointsSerializer
from django.shortcuts import get_object_or_404
from app.gamification.models.xp_points import XpPoints
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class UpdateExp(generics.RetrieveUpdateAPIView):
    queryset = XpPoints.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = XpPointsSerializer

    @swagger_auto_schema(
        operation_description="Update user's exp and level",
        tags=['exp'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'operation': openapi.Schema(type=openapi.TYPE_STRING, description='operation name'),
                'method': openapi.Schema(type=openapi.TYPE_STRING, description='method name'),
                'api': openapi.Schema(type=openapi.TYPE_STRING, description='api name'),
            }
        ),
        responses={
            200: openapi.Response(
                description='User\'s exp and level updated',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'exp': openapi.Schema(type=openapi.TYPE_INTEGER, description='user\'s exp'),
                        'level': openapi.Schema(type=openapi.TYPE_INTEGER, description='user\'s level'),
                    }
                )
            ),
            400: openapi.Response(
                description='User has already gained exp for this operation',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='error message'),
                    }
                )
            ),
            403: openapi.Response(
                description='User is not authenticated',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='error message'),
                    }
                )
            ),
        }
    )
    def patch(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        operation = request.data.get('operation')
        method = request.data.get('method')
        api = request.data.get('api')

        # check if user has already gained exp by this operation
        try:
            exp_history = ExpHistory.objects.get(
                user=user, method=method, api=api)
            return Response(data={'error': 'User has gained points for this operation'}, status=status.HTTP_400_BAD_REQUEST)
        # if not, update the exp and create a new exp history
        except ExpHistory.DoesNotExist:
            exp_history = ExpHistory.objects.create(
                user=user, method=method, api=api)
            exp_history.save()
        try:
            behavior = Behavior.objects.get(operation=operation)
        except Behavior.DoesNotExist:
            return Response(data={'error': 'Behavior not found'}, status=status.HTTP_400_BAD_REQUEST)
        points = behavior.points
        try:
            xp_points = XpPoints.objects.get(user=user)
        except XpPoints.DoesNotExist:
            xp_points = XpPoints.objects.create(user=user)
        xp_points.exp_points += points
        required_exp = level_func(xp_points.level)
        if xp_points.exp + points >= required_exp:
            xp_points.level += 1
            xp_points.exp = xp_points.exp + points - required_exp
        else:
            xp_points.exp += points
        xp_points.save()
        serializer = self.get_serializer(xp_points)
        data = serializer.data
        data["operation"] = operation
        data["gain"] = points
        return Response(data)
