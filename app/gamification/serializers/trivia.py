from rest_framework import serializers
from app.gamification.models import Trivia

class TriviaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trivia
        fields = ['id', 'question', 'hints', 'course']