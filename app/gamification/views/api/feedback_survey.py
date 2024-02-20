import copy
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models.assignment import Assignment
from app.gamification.models.feedback_survey import FeedbackSurvey
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question import Question
from app.gamification.models.survey_section import SurveySection
from app.gamification.models.survey_template import SurveyTemplate
from app.gamification.models.trivia import Trivia
from app.gamification.serializers.survey import SurveySerializer


class SurveyList(generics.ListCreateAPIView):
    serializer_class = SurveySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get survey information", tags=["surveys"])
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        feedback_survey = FeedbackSurvey.objects.filter(assignment=assignment).order_by('pk').last()
        if feedback_survey is None:
            return Response({"messages": "Feedback Survey does not exist"}, status=status.HTTP_404_NOT_FOUND)
        survey_template = feedback_survey.template
        context = {
            "course_id": course_id,
            "assignment_id": assignment_id,
            "survey_template_name": survey_template.name,
            "survey_template_instruction": survey_template.instructions,
            "feedback_survey_date_released": feedback_survey.date_released,
            "feedback_survey_date_due": feedback_survey.date_due,
        }
        return Response(context, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new survey, template_name is \
        'default template' will create a default template based on fixture data",
        tags=["surveys"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "template_name": openapi.Schema(type=openapi.TYPE_STRING),
                "instructions": openapi.Schema(type=openapi.TYPE_STRING),
                "date_released": openapi.Schema(type=openapi.TYPE_STRING),
                "date_due": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request, course_id, assignment_id, *args, **kwargs):
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        # Get survey_id. If survey_id is -1, it means we are using a template,
        # hence we need to deepcopy the sections and questions
        survey_id = request.data.get("survey_id")
        is_using_template = False

        # Using a template
        if survey_id is not None and survey_id != -1:
            # Reuse template
            is_using_template = True
            survey_template = SurveyTemplate.objects.get(id=survey_id)
            survey_sections = survey_template.sections.all()

        # Get request parameters
        user_id = request.data.get("user_id")
        survey_template_name = request.data.get("template_name").strip()
        survey_template_instructions = request.data.get("instructions")
        trivia_data = request.data.get("trivia")
        trivia = None
        if trivia_data is not None and "question" in trivia_data and "answer" in trivia_data:
            trivia = Trivia(
                question=trivia_data["question"],
                answer=trivia_data["answer"],
                hints=trivia_data["hints"],
            )
            trivia.save()
        feedback_survey_date_released = request.data.get("date_released")
        feedback_survey_date_due = request.data.get("date_due")

        # Create a new survey
        survey_template = SurveyTemplate(
            user_id=user_id,
            course_id=course_id,
            name=survey_template_name,
            instructions=survey_template_instructions,
            trivia=trivia,
        )
        survey_template.save()

        # Copy from existing survey, no need to create an artifact section
        if is_using_template:
            new_survey_sections = copy.deepcopy(survey_sections)
            for new_section in new_survey_sections:
                questions = Question.objects.filter(section=new_section.pk)
                # Clear the primary key
                new_section.pk = None
                new_section.template = survey_template
                new_section.save()

                # Iterate through questions of the copied section
                for question in questions:
                    new_question = copy.deepcopy(question)
                    new_question.pk = None
                    new_question.section = new_section
                    new_question.save()
        else:
            # Create the artifact section
            SurveySection.objects.create(
                template=survey_template,
                title="Artifact",
                description="Please review the artifact.",
                is_required=False,
            )

        response_data = {
            "template_name": survey_template_name,
            "instructions": survey_template_instructions,
            "date_released": feedback_survey_date_released,
            "date_due": feedback_survey_date_due
        }

        feedback_survey = FeedbackSurvey(
            assignment=assignment,
            template=survey_template,
            date_released=feedback_survey_date_released,
            date_due=feedback_survey_date_due,
        )

        feedback_survey.save()
        self.serializer_class(survey_template)

        return Response(response_data, status=status.HTTP_201_CREATED)


class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SurveyTemplate.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get a survey template",
        tags=["surveys"],
    )
    def get(self, request, feedback_survey_pk, *args, **kwargs):
        survey = get_object_or_404(SurveyTemplate, id=feedback_survey_pk)
        serializer = self.get_serializer(survey)
        return Response(serializer.data)

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
    def patch(self, request, feedback_survey_pk, *args, **kwargs):
        survey = get_object_or_404(SurveyTemplate, id=feedback_survey_pk)
        name = request.data.get("template_name").strip()
        if name == "":
            content = {"message": "Survey name cannot be empty"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("trivia"):
            trivia_data = request.data.get("trivia")
            if "id" in trivia_data:
                trivia = get_object_or_404(Trivia, id=trivia_data["id"])
                trivia.question = trivia_data["question"]
                trivia.answer = trivia_data["answer"]
                trivia.hints = trivia_data["hints"]
            else:
                trivia = Trivia(
                    question=trivia_data["question"],
                    answer=trivia_data["answer"],
                    hints=trivia_data["hints"],
                )
            trivia.save()
            survey.trivia = trivia
        elif survey.trivia is not None:
            survey.trivia.delete()

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
    def delete(self, request, feedback_survey_pk, *args, **kwargs):
        survey = get_object_or_404(SurveyTemplate, id=feedback_survey_pk)
        survey.delete()
        return Response(status=204)
