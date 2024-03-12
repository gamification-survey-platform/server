import copy
from django.shortcuts import get_object_or_404
from app.gamification.models.artifact import Artifact
from app.gamification.models.artifact_review import ArtifactReview
from app.gamification.models.user import CustomUser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models.assignment import Assignment
from app.gamification.models.survey import FeedbackSurvey
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question import Question
from app.gamification.models.survey_section import SurveySection
from app.gamification.models.trivia import Trivia
from app.gamification.serializers.survey import SurveySerializer


class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FeedbackSurvey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get a survey template",
        tags=["surveys"],
    )
    def get(self, request, survey_pk, *args, **kwargs):
        survey_template = get_object_or_404(FeedbackSurvey, id=survey_pk)
        data = dict()
        data["pk"] = survey_template.pk
        data["name"] = survey_template.name
        data["instructions"] = survey_template.instructions
        data["sections"] = []
        for section in survey_template.sections:
            curr_section = dict()
            curr_section["pk"] = section.pk
            curr_section["title"] = section.title
            curr_section["is_required"] = section.is_required
            curr_section["questions"] = []
            for question in section.questions:
                curr_question = dict()
                curr_question["pk"] = question.pk
                curr_question["text"] = question.text
                curr_question["is_required"] = question.is_required
                curr_question["phrased_positively"] = question.phrased_positively
                curr_question["gamified"] = question.gamified
                curr_question["question_type"] = question.question_type
                if (
                    question.question_type == Question.QuestionType.MULTIPLECHOICE
                    or question.question_type == Question.QuestionType.MULTIPLESELECT
                ):
                    curr_question["option_choices"] = []
                    for option_choice in question.options:
                        curr_option_choice = dict()
                        curr_option_choice["pk"] = option_choice.pk
                        curr_option_choice["text"] = option_choice.text
                        curr_question["option_choices"].append(curr_option_choice)
                elif question.question_type == Question.QuestionType.SCALEMULTIPLECHOICE:
                    curr_question["number_of_scale"] = question.number_of_scale
                else:
                    curr_question["number_of_text"] = question.number_of_text
                curr_section["questions"].append(curr_question)
            data["sections"].append(curr_section)
        return Response(data)

    @swagger_auto_schema(
        operation_description="Update a survey template",
        tags=["surveys"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "template_name": openapi.Schema(type=openapi.TYPE_STRING),
                "instructions": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def patch(self, request, survey_pk, *args, **kwargs):
        survey = get_object_or_404(FeedbackSurvey, id=survey_pk)
        name = request.data.get("template_name").strip()
        if name == "":
            content = {"message": "Survey name cannot be empty"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        instructions = request.data.get("instructions")
        survey.name = name
        survey.instructions = instructions
        survey.save()
        serializer = self.get_serializer(survey)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Delete a survey template",
        tags=["surveys"],
    )
    def delete(self, request, survey_pk, *args, **kwargs):
        survey = get_object_or_404(FeedbackSurvey, id=survey_pk)
        survey.delete()
        return Response(status=204)
