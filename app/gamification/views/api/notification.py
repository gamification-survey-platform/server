from django.forms import model_to_dict
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models import CustomUser, Notification, Registration
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
        receiver_id = request.data.get("receiver")
        type = request.data.get("type")
        text = request.data.get("text")
        available_types = [type.name for type in Notification.NotificationType]
        if receiver_id is None:
            return Response({"message": "Notification has no receiver."}, status=status.HTTP_400_BAD_REQUEST)
        if type not in available_types:
            return Response({"message": "Invalid notification type."}, status=status.HTTP_400_BAD_REQUEST)
        if receiver_id.isnumeric():
            receiver_registration = Registration.objects.get(pk=receiver_id)
            receiver = receiver_registration.user
        else:
            receiver = CustomUser.objects.get(andrew_id=receiver_id)
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
            Notification.objects.filter(receiver=user), key=lambda notification: notification.timestamp
        )
        print(notifications)
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
        print(response_data)
        return Response(response_data)
