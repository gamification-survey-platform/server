from rest_framework import serializers

from app.gamification.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["pk", "sender", "receiver", "text", "type"]
