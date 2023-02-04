from rest_framework import serializers

from app.gamification.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['andrew_id', 'first_name', 'last_name',
                  'email', 'is_staff', 'is_active', 'date_joined']
