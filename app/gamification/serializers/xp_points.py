from rest_framework import serializers

from app.gamification.models import XpPoints


class XpPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = XpPoints
        fields = ['pk', 'user', 'exp_points', 'exp', 'level']
