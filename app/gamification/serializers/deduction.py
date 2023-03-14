from rest_framework import serializers

from app.gamification.models import Deduction


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = ['pk', 'grade', 'deduction_score', 'title', 'description', 'timestamp']
