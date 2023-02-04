from rest_framework import serializers

from app.gamification.models import Answer, ArtifactReview, ArtifactFeedback
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question import Question
from app.gamification.models.question_option import QuestionOption


class CreateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['pk', 'question_option', 'artifact_review', 'answer_text']


class QuestionOnlyHavePkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['pk']


class QuestionOptionSerializer(serializers.ModelSerializer):
    question = QuestionOnlyHavePkSerializer()

    class Meta:
        model = QuestionOption
        fields = ['number_of_text', 'question']


class AnswerSerializer(serializers.ModelSerializer):
    question_option = QuestionOptionSerializer()

    class Meta:
        model = Answer
        fields = ['pk', 'question_option', 'artifact_review', 'answer_text']


class ArtifactFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtifactFeedback
        fields = ['pk', 'question_option',
                  'artifact_review', 'answer_text', 'page']


class ArtifactReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtifactReview
        fields = ['pk', 'artifact', 'user']
