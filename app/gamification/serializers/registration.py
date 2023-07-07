from rest_framework import serializers

from app.gamification.models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ["user", "course"]
