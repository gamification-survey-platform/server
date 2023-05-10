from rest_framework import serializers

from app.gamification.models import Entity


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ["pk", "course", "registration", "members"]
