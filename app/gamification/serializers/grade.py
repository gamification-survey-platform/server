from rest_framework import serializers

from app.gamification.models import Grade


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['pk', 'artifact', 'grade_title', 'score', 'timestamp']
