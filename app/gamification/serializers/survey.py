from rest_framework import serializers

from app.gamification.models import SurveySection, SurveyTemplate
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question import Question


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyTemplate
        fields = ["pk", "name", "instructions"]


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySection
        fields = ["pk", "template", "title", "description", "is_required"]


class TemplateSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySection
        fields = ["pk", "template", "title", "description", "is_required"]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "pk",
            "section",
            "text",
            "is_required",
            "is_multiple",
            "dependent_question",
            "question_type",
            "option_choices",
            "number_of_scale",
        ]


class OptionChoiceWithoutNumberOfTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionChoice
        fields = ["pk", "text"]


class OptionChoiceSerializer(serializers.ModelSerializer):
    number_of_text = serializers.IntegerField()

    class Meta:
        model = OptionChoice
        fields = ["pk", "text", "number_of_text"]


class SurveySectionSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True)

    class Meta:
        model = SurveyTemplate
        fields = ["pk", "name", "instructions", "sections"]


class SectionQuestionsSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = SurveySection
        fields = ["pk", "template", "title", "description", "is_required", "questions"]
