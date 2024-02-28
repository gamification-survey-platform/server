import copy
from datetime import datetime

from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models import Assignment, Course, CustomUser
from app.gamification.models.artifact import Artifact
from app.gamification.models.artifact_review import ArtifactReview
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question import Question
from app.gamification.models.survey import FeedbackSurvey
from app.gamification.models.survey_section import SurveySection
from app.gamification.serializers import AssignmentSerializer
from app.gamification.serializers.survey import SurveySerializer
from app.gamification.utils.auth import get_user_pk


class AssignmentSurvey(generics.ListCreateAPIView):
    serializer_class = SurveySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get survey information", tags=["surveys"])
    def get(self, request, assignment_id, *args, **kwargs):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        survey = assignment.survey
        if survey is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )
        data = dict()
        data["pk"] = survey.pk
        data["name"] = survey.name
        data["instructions"] = survey.instructions
        data["sections"] = []
        data["trivia"] = None
        for section in survey.sections:
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
    def post(self, request, assignment_id, *args, **kwargs):
        # Get survey_id from the request. If survey_id is -1, it means we are using a template,
        # hence we need to deepcopy the sections and questions
        survey_id = request.data.get("survey_id")
        is_using_template = False

        # Using a template
        if survey_id is not None and survey_id != -1:
            # Reuse template
            is_using_template = True
            survey_template = FeedbackSurvey.objects.get(id=survey_id)
            survey_sections = survey_template.sections.all()

        # Get request parameters
        user_id = request.data.get("user_id")
        survey_name = request.data.get("template_name").strip()
        survey_instructions = request.data.get("instructions")
        feedback_survey_date_released = request.data.get("date_released")
        feedback_survey_date_due = request.data.get("date_due")

        # Create a new survey
        feedback_survey = FeedbackSurvey(
            assignment_id=assignment_id,
            user_id=user_id,
            name=survey_name,
            instructions=survey_instructions,
            date_released=feedback_survey_date_released,
            date_due=feedback_survey_date_due,
        )
        feedback_survey.save()

        # Copy from existing survey, no need to create an artifact section
        if is_using_template:
            new_survey_sections = copy.deepcopy(survey_sections)
            for new_section in new_survey_sections:
                questions = Question.objects.filter(section=new_section.pk)
                # Clear the primary key
                new_section.pk = None
                new_section.survey = feedback_survey
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
                survey=feedback_survey,
                title="Artifact",
                description="Please review the artifact.",
                is_required=False,
            )

        response_data = {
            "template_name": survey_name,
            "instructions": survey_instructions,
            "date_released": feedback_survey_date_released,
            "date_due": feedback_survey_date_due
        }
        self.serializer_class(feedback_survey)

        return Response(response_data, status=status.HTTP_201_CREATED)

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
    def patch(self, request, assignment_id, *args, **kwargs):
        survey_info = request.data.get("survey_info")
        survey = get_object_or_404(FeedbackSurvey, id=survey_info["pk"])
        sections = SurveySection.objects.filter(survey=survey)
        # Update all artifact reviews with the survey template to be INCOMPLETE
        assignment = get_object_or_404(Assignment, id=assignment_id)
        artifacts = Artifact.objects.filter(assignment=assignment)
        for artifact in artifacts:
            artifact_reviews = ArtifactReview.objects.filter(artifact=artifact)
            for artifact_review in artifact_reviews:
                if artifact_review.status == ArtifactReview.ArtifactReviewType.COMPLETED:
                    return Response(
                        {"message": "Cannot modify survey that has already been completed."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

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
            section_template.survey = survey
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
                if question["question_type"] == Question.QuestionType.NUMBER:
                    question_template.min = question["min"] if "min" in question else 0
                    question_template.max = question["max"] if "max" in question else 100

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


class AssignmentList(generics.ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get all assignments information",
        tags=["assignments"],
        responses={
            200: openapi.Response(
                description="Each assignment details with user role",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "course": openapi.Schema(type=openapi.TYPE_INTEGER, description="course id"),
                            "assignment_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                            "assignment_type": openapi.Schema(type=openapi.TYPE_STRING, enum=["Individual", "Team"]),
                            "submission_type": openapi.Schema(type=openapi.TYPE_STRING, enum=["File", "URL", "Text"]),
                            "total_score": openapi.Schema(type=openapi.TYPE_NUMBER),
                            "weight": openapi.Schema(type=openapi.TYPE_NUMBER),
                            "date_released": openapi.Schema(type=openapi.TYPE_STRING),
                            "date_due": openapi.Schema(type=openapi.TYPE_STRING),
                            "user_role": openapi.Schema(type=openapi.TYPE_STRING, enum=["Student", "TA", "Instructor"]),
                        },
                    ),
                ),
            )
        },
    )
    def get(self, request, course_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        course = get_object_or_404(Course, pk=course_id)
        assignments = Assignment.objects.filter(course=course)
        assignments = [model_to_dict(assignment) for assignment in assignments]
        response_data = []
        for assignment in assignments:
            # DEBUG
            # if (
            #     datetime.now().astimezone(pytz.timezone("America/Los_Angeles")) >= assignment["date_released"]
            #     or user.is_staff
            # ):
            #     assignment["is_staff"] = user.is_staff
            #     response_data.append(assignment)
            assignment["is_staff"] = user.is_staff
            response_data.append(assignment)
            ##
        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new assignment",
        tags=["assignments"],
    )
    def post(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        assignment_name = request.data.get("assignment_name")
        assignment_type = request.data.get("assignment_type")
        date_released = request.data.get("date_released")
        date_due = request.data.get("date_due")
        description = request.data.get("description")
        submission_type = request.data.get("submission_type")
        total_score = request.data.get("total_score")
        weight = request.data.get("weight")
        min_reviewers = request.data.get("min_reviewers")
        review_assign_policy = request.data.get("review_assign_policy")
        if user.is_staff:
            assignment = Assignment.objects.create(
                course=course,
                assignment_name=assignment_name,
                assignment_type=assignment_type,
                date_released=date_released,
                date_due=date_due,
                description=description,
                submission_type=submission_type,
                total_score=total_score,
                weight=weight,
                review_assign_policy=review_assign_policy,
                min_reviewers=min_reviewers,
            )
            assignment.save()
            data = model_to_dict(assignment)
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class AssignmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get assignment information",
        tags=["assignments"],
        responses={
            200: openapi.Schema(
                description="Assignment details with user role",
                type=openapi.TYPE_OBJECT,
                properties={
                    "pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "course": openapi.Schema(type=openapi.TYPE_INTEGER, description="course id"),
                    "assignment_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                    "assignment_type": openapi.Schema(type=openapi.TYPE_STRING, enum=["Individual", "Team"]),
                    "submission_type": openapi.Schema(type=openapi.TYPE_STRING, enum=["File", "URL", "Text"]),
                    "total_score": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "weight": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "date_released": openapi.Schema(type=openapi.TYPE_STRING),
                    "date_due": openapi.Schema(type=openapi.TYPE_STRING),
                    "user_role": openapi.Schema(type=openapi.TYPE_STRING, enum=["Student", "TA", "Instructor"]),
                },
            )
        },
    )
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        data = model_to_dict(assignment)
        data["is_staff"] = user.is_staff
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="update an assignment",
        tags=["assignments"],
    )
    def patch(self, request, course_id, assignment_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        assignment_name = request.data.get("assignment_name")
        assignment_type = request.data.get("assignment_type")
        date_due = request.data.get("date_due")
        date_released = request.data.get("date_released")
        description = request.data.get("description")
        submission_type = request.data.get("submission_type")
        total_score = request.data.get("total_score")
        weight = request.data.get("weight")
        review_assign_policy = request.data.get("review_assign_policy")
        if user.is_staff:
            try:
                assignment = Assignment.objects.get(pk=assignment_id)
            except Assignment.DoesNotExist:
                assignment = Assignment()
            assignment.course = course
            assignment.assignment_name = assignment_name
            assignment.assignment_type = assignment_type
            assignment.date_due = date_due
            assignment.date_released = date_released
            assignment.description = description
            assignment.submission_type = submission_type
            assignment.total_score = total_score
            assignment.weight = weight
            assignment.review_assign_policy = review_assign_policy
            assignment.save()
            data = model_to_dict(assignment)
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description="Delete an assignment",
        tags=["assignments"],
    )
    def delete(self, request, course_id, assignment_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        if user.is_staff:
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            assignment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
