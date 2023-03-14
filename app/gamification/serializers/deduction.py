from rest_framework import serializers

from app.gamification.models import Deduction


class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = ['pk', 'grade', 'deduction_score', 'title', 'description', 'timestamp']
