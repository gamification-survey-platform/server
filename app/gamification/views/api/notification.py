import json

from django.forms import model_to_dict
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models import (
    ArtifactReview,
    CustomUser,
    Notification,
    Registration,
)
from app.gamification.models.behavior import Behavior
from app.gamification.serializers import NotificationSerializer
from app.gamification.utils.auth import get_user_pk


class NotificationDetail(generics.GenericAPIView):
    queryset = Notification.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = NotificationSerializer

    @swagger_auto_schema(
        operation_description="Create a notification",
        tags=["notifications"],
        responses={
            200: openapi.Response(
                description="Create notification",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "type": openapi.Schema(type=openapi.TYPE_STRING),
                        "sender": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "receiver": openapi.Schema(type=openapi.TYPE_STRING),
                        "text": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
            )
        },
    )
    def post(self, request, *args, **kwargs):
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        # adding points for poke
        behavior = Behavior.objects.get(operation="poke")
        user.exp += behavior.points
        user.save()
        receiver_id = request.data.get("receiver")
        type = request.data.get("type")
        text = request.data.get("text")
        available_types = [type.name for type in Notification.NotificationType]
        if receiver_id is None:
            return Response({"message": "Notification has no receiver."}, status=status.HTTP_400_BAD_REQUEST)
        if type not in available_types:
            return Response({"message": "Invalid notification type."}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(receiver_id, int):
            if type == Notification.NotificationType.POKE:
                receiver_registration = Registration.objects.get(pk=receiver_id)
                receiver = receiver_registration.user
            else:
                receiver = CustomUser.objects.get(pk=receiver_id)
        else:
            receiver = CustomUser.objects.get(andrew_id=receiver_id)
        # If FEEDBACK_RESPONSE, delete the FEEDBACK_REQUEST
        if type == Notification.NotificationType.FEEDBACK_RESPONSE:
            data = json.loads(request.data.get("text"))
            feedback_request_id = data["feedback_request_id"]
            feedback_request = Notification.objects.get(id=feedback_request_id)
            feedback_request.delete()
            del data["feedback_request_id"]
            artifact_review_id = data["artifact_review"]
            del data["artifact_review"]
            artifact_review = ArtifactReview.objects.get(id=artifact_review_id)
            artifact_id = artifact_review.artifact.id
            data["artifact"] = artifact_id
            if "answer_text" in data:
                del data["answer_text"]
            text = json.dumps(data)
        notification = Notification.objects.create(sender=user, receiver=receiver, type=type, text=text)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Get all notifications",
        tags=["notifications"],
        responses={
            200: openapi.Response(
                description="Get all notifications and mark unread ones as read",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "type": openapi.Schema(type=openapi.TYPE_STRING),
                            "sender": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "receiver": openapi.Schema(type=openapi.TYPE_STRING),
                            "text": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        },
                    ),
                ),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        user_pk = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_pk)
        notifications = sorted(
            Notification.objects.filter(receiver=user), key=lambda notification: notification.timestamp, reverse=True
        )
        response_data = []
        for i, notification in enumerate(notifications):
            # Only maintain 10 latest notifications
            if i >= 10:
                notification.delete()
                continue
            notification_data = model_to_dict(notification)
            notification_data["sender_andrew_id"] = notification.sender.andrew_id
            notification_data["receiver_andrew_id"] = notification.receiver.andrew_id
            notification_data["timestamp"] = notification.timestamp
            response_data.append(notification_data)
            # Mark all unread notifications as read
            if not notification.is_read:
                notification.is_read = True
                notification.save()
        return Response(response_data)
