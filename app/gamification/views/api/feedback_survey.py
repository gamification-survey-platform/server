import json
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from app.gamification.models.assignment import Assignment
from app.gamification.models.feedback_survey import FeedbackSurvey
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question import Question
from app.gamification.models.question_option import QuestionOption
from app.gamification.models.registration import Registration
from app.gamification.models.survey_section import SurveySection
from app.gamification.models.survey_template import SurveyTemplate
from app.gamification.serializers.survey import OptionChoiceSerializer, OptionChoiceWithoutNumberOfTextSerializer, QuestionSerializer, SectionSerializer, SurveySerializer, TemplateSectionSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class SurveyList(generics.ListCreateAPIView):
    serializer_class = SurveySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get survey information",
        tags=['surveys']
    )
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        try:
            feedback_survey = FeedbackSurvey.objects.get(assignment=assignment)
        except FeedbackSurvey.DoesNotExist:
            return Response({"messages": "Feedback Survey does not exist"}, status=status.HTTP_404_NOT_FOUND)
        survey_template = feedback_survey.template
        context = {
            'course_id': course_id,
            'assignment_id': assignment_id,
            'survey_template_name': survey_template.name,
            'survey_template_instruction': survey_template.instructions,
            'survey_template_other_info': survey_template.other_info,
            'feedback_survey_date_released': feedback_survey.date_released,
            'feedback_survey_date_due': feedback_survey.date_due
        }
        return Response(context, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new survey, template_name is 'default template' will create a default template based on fixture data",
        tags=['surveys'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'template_name': openapi.Schema(type=openapi.TYPE_STRING),
                'instructions': openapi.Schema(type=openapi.TYPE_STRING),
                'other_info': openapi.Schema(type=openapi.TYPE_STRING),
                'date_released': openapi.Schema(type=openapi.TYPE_STRING),
                'date_due': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request, assignment_id, *args, **kwargs):
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        survey_template_name = request.data.get('template_name').strip()
        survey_template_instructions = request.data.get('instructions')
        survey_template_other_info = request.data.get('other_info')
        feedback_survey_date_released = request.data.get('date_released')
        feedback_survey_date_due = request.data.get('date_due')
        response_data = {
            'template_name': survey_template_name,
            'instructions': survey_template_instructions,
            'other_info': survey_template_other_info,
            'date_released': feedback_survey_date_released,
            'date_due': feedback_survey_date_due
        }

        feedback_survey = FeedbackSurvey.objects.filter(assignment=assignment)
        # Check if feedback survey exists
        if feedback_survey.exists():
            survey_template = feedback_survey[0].template
            survey_template.name = survey_template_name
            survey_template.instructions = survey_template_instructions
            survey_template.other_info = survey_template_other_info
            survey_template.save()
            # Create new survey
            feedback_survey[0].template = survey_template
            feedback_survey[0].date_released = feedback_survey_date_released
            feedback_survey[0].date_due = feedback_survey_date_due
            feedback_survey[0].save()
            return Response(response_data, status=status.HTTP_200_OK)

        # Create new template
        survey_template = SurveyTemplate(
            name=survey_template_name, instructions=survey_template_instructions, other_info=survey_template_other_info)
        survey_template.save()
        feedback_survey = FeedbackSurvey(
            assignment=assignment,
            template=survey_template,
            date_released=feedback_survey_date_released,
            date_due=feedback_survey_date_due
        )
        feedback_survey.save()

        if survey_template_name == "Default Template":
            default_survey_template = get_object_or_404(
                SurveyTemplate, is_template=True, name="Survey Template")
            for default_section in default_survey_template.sections:
                section = SurveySection(template=survey_template,
                                        title=default_section.title,
                                        description=default_section.description,
                                        is_required=default_section.is_required,
                                        )
                section.save()
                for default_question in default_section.questions:
                    question = Question(section=section,
                                        text=default_question.text,
                                        question_type=default_question.question_type,
                                        dependent_question=default_question.dependent_question,
                                        is_required=default_question.is_required,
                                        is_multiple=default_question.is_multiple,
                                        )
                    question.save()
                    for default_option in default_question.options:
                        question_option = QuestionOption(
                            question=question,
                            option_choice=default_option.option_choice,
                            number_of_text=default_option.number_of_text,
                        )
                        question_option.save()
        # Automatically create a section and question for artifact
        else:
            artifact_section = SurveySection.objects.create(
                template=survey_template,
                title='Artifact',
                description='Please review the artifact.',
                is_required=False,
            )
            artifact_question = Question.objects.create(
                section=artifact_section,
                text='',
                question_type=Question.QuestionType.SLIDEREVIEW,
            )
            empty_option, _ = OptionChoice.objects.get_or_create(text='')
            QuestionOption.objects.create(
                question=artifact_question, option_choice=empty_option)
            self.serializer_class(survey_template)

        return Response(response_data, status=status.HTTP_201_CREATED)


class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SurveyTemplate.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get a survey template",
        tags=['surveys'],
    )
    def get(self, request, feedback_survey_pk, *args, **kwargs):
        survey = get_object_or_404(SurveyTemplate, id=feedback_survey_pk)
        serializer = self.get_serializer(survey)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a survey template",
        tags=['surveys'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'template_name': openapi.Schema(type=openapi.TYPE_STRING),
                'instructions': openapi.Schema(type=openapi.TYPE_STRING),
                'other_info': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def put(self, request, feedback_survey_pk, *args, **kwargs):
        survey = get_object_or_404(SurveyTemplate, id=feedback_survey_pk)
        name = request.data.get('template_name').strip()
        if name == '':
            content = {'message': 'Survey name cannot be empty'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        instructions = request.data.get('instructions')
        other_info = request.data.get('other_info')
        survey.name = name
        survey.instructions = instructions
        survey.other_info = other_info
        survey.save()
        serializer = self.get_serializer(survey)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Delete a survey template",
        tags=['surveys'],
    )
    def delete(self, request, feedback_survey_pk, *args, **kwargs):
        survey = get_object_or_404(SurveyTemplate, id=feedback_survey_pk)
        survey.delete()
        return Response(status=204)
