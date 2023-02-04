from rest_framework import serializers

from app.gamification.models import Constraint, Progress,Rule


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ['default', 'name', 'description']