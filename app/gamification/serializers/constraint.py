from rest_framework import serializers

from app.gamification.models import Constraint, Progress

class ConstraintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constraint
        fields = ['pk', 'url', 'threshold']

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ['pk', 'met', 'cur_point', 'constraint', 'user']