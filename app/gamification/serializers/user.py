from rest_framework import serializers

from app.gamification.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "pk",
            "andrew_id",
            "first_name",
            "last_name",
            "exp",
            "email",
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
        ]
