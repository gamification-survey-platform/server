from rest_framework import serializers

from app.gamification.models import Answer, ArtifactFeedback, ArtifactReview
from app.gamification.models.question import Question


class CreateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["pk", "option_choice", "artifact_review", "answer_text"]


class QuestionOnlyHavePkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["pk"]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["pk", "option_choice", "artifact_review", "answer_text"]


class ArtifactFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtifactFeedback
        fields = ["pk", "option_choice", "artifact_review", "answer_text", "page"]


class ArtifactReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtifactReview
        fields = ["pk", "artifact", "user", "status"]
