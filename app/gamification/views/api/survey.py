from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.response import Response

from app.gamification.models.assignment import Assignment
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question import Question
from app.gamification.models.survey_section import SurveySection
from app.gamification.models.survey_template import SurveyTemplate
from app.gamification.serializers.survey import SurveySerializer


class SurveyGetInfo(generics.RetrieveUpdateAPIView):
    queryset = SurveyTemplate.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.AllowAny]  # [IsAdminOrReadOnly]

    @swagger_auto_schema(
        operation_description="Get feedback survey information and contents",
        tags=["surveys"],
        responses={
            200: openapi.Response(
                description="Survey information",
                schema=SurveySerializer,
            ),
        },
    )
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        survey_template = assignment.survey_template
        data = dict()
        data["pk"] = survey_template.pk
        data["name"] = survey_template.name
        data["instructions"] = survey_template.instructions
        data["other_info"] = survey_template.other_info
        data["sections"] = []
        data["trivia"] = None
        if survey_template.trivia is not None:
            data["trivia"] = model_to_dict(survey_template.trivia)
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
        operation_description="Update feedback survey information and contents",
        tags=["surveys"],
        responses={
            200: openapi.Response(
                description="Survey information",
                schema=SurveySerializer,
            ),
        },
    )
    def patch(self, request, course_id, assignment_id, *args, **kwargs):
        survey_info = request.data.get("survey_info")
        survey_template = get_object_or_404(SurveyTemplate, id=survey_info["pk"])
        sections = SurveySection.objects.filter(template=survey_template)

        # Delete all previous survey contents
        for section in sections:
            questions = Question.objects.filter(section=section)
            for question in questions:
                for option_choice in question.options.all():
                    option_choice.delete()
                for option_choice in question.options.all():
                    option_choice.delete()
                question.delete()
            section.delete()
        for section in survey_info["sections"]:
            section_template = SurveySection()
            section_template.template = survey_template
            section_template.title = section["title"]
            section_template.is_required = section["is_required"]
            section_template.save()
            for question in section["questions"]:
                question_template = Question()
                question_template.section = section_template
                question_template.text = question["text"]
                question_template.is_required = question["is_required"]
                question_template.question_type = question["question_type"]
                question_template.phrased_positively = question["phrased_positively"]
                question_template.gamified = question["gamified"]
                if question["question_type"] == Question.QuestionType.SCALEMULTIPLECHOICE:
                    question_template.number_of_scale = question["number_of_scale"]
                elif question["question_type"] == Question.QuestionType.MULTIPLETEXT:
                    question_template.number_of_text = question["number_of_text"]
                question_template.save()
                if (
                    question["question_type"] == Question.QuestionType.MULTIPLECHOICE
                    or question["question_type"] == Question.QuestionType.MULTIPLESELECT
                ):
                    for option in question_template.options:
                        option.delete()
                    for option_choice in question["option_choices"]:
                        option_choice_template = OptionChoice()
                        option_choice_template.question = question_template
                        option_choice_template.text = option_choice["text"]
                        option_choice_template.save()
                else:
                    option_choice = OptionChoice()
                    option_choice.question = question_template
                    # No text field for other Question types
                    option_choice.save()
        return Response(status=200)
