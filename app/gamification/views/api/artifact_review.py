from datetime import datetime, timedelta
import math

import pandas as pd
import pytz
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from collections import OrderedDict

from app.gamification.models.answer import Answer, ArtifactFeedback
from app.gamification.models.artifact import Artifact
from app.gamification.models.artifact_review import ArtifactReview
from app.gamification.models.assignment import Assignment
from app.gamification.models.behavior import Behavior
from app.gamification.models.course import Course
from app.gamification.models.entity import Individual, Team
from app.gamification.models.survey import FeedbackSurvey
from app.gamification.models.membership import Membership
from app.gamification.models.notification import Notification
from app.gamification.models.question import Question
from app.gamification.models.registration import Registration
from app.gamification.models.user import CustomUser
from app.gamification.models.entity import Entity
from app.gamification.serializers.answer import ArtifactReviewSerializer
from app.gamification.utils.auth import get_user_pk
from app.gamification.utils.levels import inv_level_func, level_func
from django.db.models import Count
import random

base_artifact_review_schema = {
    "sections": openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                "questions": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "answer": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "text": openapi.Schema(type=openapi.TYPE_STRING),
                                        "page": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    },
                                ),
                            ),
                        },
                    ),
                ),
            },
        ),
    )
}


class AssignmentArtifactReviewList(generics.GenericAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Create specific artifact review for a student",
        tags=["artifact_reviews"],
        responses={
            200: openapi.Schema(
                description="Create artifact review for a student",
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "artifact": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "user": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "status": openapi.Schema(type=openapi.TYPE_STRING, enum=["COMPLETED", "INCOMPLETE", "LATE"]),
                    "max_artifact_review_score": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "artifact_review_score": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "reviewing": openapi.Schema(type=openapi.TYPE_STRING),
                    "course_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "assignment_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            )
        },
    )
    def post(self, request, course_id, assignment_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        reviewer_andrew_id = request.data.get("reviewer")
        print("create new reviews now:: ", reviewer_andrew_id)
        reviewee_andrew_id = request.data.get("reviewee")
        reviewer = get_object_or_404(CustomUser, andrew_id=reviewer_andrew_id)
        reviewee = get_object_or_404(CustomUser, andrew_id=reviewee_andrew_id)
        reviewer_registration = get_object_or_404(Registration, user=reviewer, course=course)
        reviewee_registration = get_object_or_404(Registration, user=reviewee, course=course)
        if assignment.assignment_type == "Individual":
            try:
                entity = Individual.objects.get(registration=reviewee_registration, course=course)
            except Individual.DoesNotExist:
                return Response({"message": "No individual found"}, status=status.HTTP_404_NOT_FOUND)
        elif assignment.assignment_type == "Team":
            try:
                entity = Team.objects.get(registration=reviewee_registration, course=course)
            except Team.DoesNotExist:
                return Response({"message": "No team found"}, status=status.HTTP_404_NOT_FOUND)
        artifact = get_object_or_404(Artifact, entity=entity)
        artifact_review = ArtifactReview(artifact=artifact, user=reviewer_registration)
        artifact_review.save()
        response_data = model_to_dict(artifact_review)
        response_data["reviewer"] = reviewer_andrew_id
        response_data["reviewing"] = reviewee_andrew_id
        return Response(response_data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Get artifact reviews for a specific assignment",
        tags=["artifact_reviews"],
        responses={
            200: openapi.Schema(
                description="List of artifact reviews for a user in an assignment",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "artifact": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "user": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "status": openapi.Schema(type=openapi.TYPE_STRING, enum=["COMPLETED", "INCOMPLETE", "LATE"]),
                        "max_artifact_review_score": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "artifact_review_score": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "reviewing": openapi.Schema(type=openapi.TYPE_STRING),
                        "course_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "assignment_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            )
        },
    )
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        course = get_object_or_404(Course, id=course_id)
        assignment = get_object_or_404(Assignment, id=assignment_id)
        feedback_survey = FeedbackSurvey.objects.filter(assignment=assignment)
        registration = get_object_or_404(Registration, user=user, course=course)
        artifacts = Artifact.objects.filter(assignment_id=assignment_id)
        response_data = []
        # Instructors get all artifacts for assignment
        if user.is_staff:
            for artifact in artifacts:
                artifact_reviews = ArtifactReview.objects.filter(artifact=artifact)
                for artifact_review in artifact_reviews:
                    artifact_review_dict = model_to_dict(artifact_review)
                    reviewer_registration = artifact_review.user
                    reviewer = get_object_or_404(CustomUser, id=reviewer_registration.user_id)
                    artifact_review_dict["reviewer"] = reviewer.andrew_id
                    if assignment.assignment_type == "Individual":
                        artifact_review_dict["reviewing"] = Membership.objects.get(
                            entity=artifact.entity
                        ).student.user.andrew_id
                        artifact_review_dict["assignment_type"] = "Team"

                    else:
                        artifact_review_dict["reviewing"] = artifact.entity.team.name
                        artifact_review_dict["assignment_type"] = "Individual"
                    artifact_review_dict["course_id"] = registration.course_id
                    artifact_review_dict["course_number"] = course.course_number
                    artifact_review_dict["assignment_id"] = assignment.id
                    response_data.append(artifact_review_dict)
        # Students get all artifacts he/she should review
        else:
            if len(feedback_survey) == 0:
                return Response({"message": "No feedback survey found"}, status=status.HTTP_404_NOT_FOUND)
            if feedback_survey[0].date_released.astimezone(pytz.timezone("America/Los_Angeles")) > datetime.now().astimezone(pytz.timezone("America/Los_Angeles")):
                return Response({"message": "Feedback survey not released yet"}, status=status.HTTP_404_NOT_FOUND)
            for artifact in artifacts:
                # Prevent self review
                artifact_members = artifact.entity.members
                # print("178", feedbackSurvey[0].date_released.astimezone(pytz.timezone("America/Los_Angeles")), " ", datetime.now().astimezone(pytz.timezone("America/Los_Angeles")))
                if user in artifact_members:
                    continue
                try:
                    artifact_review = ArtifactReview.objects.get(artifact=artifact, user=registration)
                except ArtifactReview.DoesNotExist:
                    continue
                    # artifact_review = ArtifactReview(artifact=artifact, user=registration)
                    # if save() here, it will create a new artifact review for each artifact
                    # artifact_review.save()
                if artifact_review.status == ArtifactReview.ArtifactReviewType.COMPLETED:
                    continue

                artifact_review_dict = model_to_dict(artifact_review)
                if assignment.assignment_type == "Individual":
                    artifact_review_dict["reviewing"] = Membership.objects.get(
                        entity=artifact.entity
                    ).student.user.andrew_id
                    artifact_review_dict["assignment_type"] = "Individual"
                else:
                    artifact_review_dict["reviewing"] = artifact.entity.team.name
                    artifact_review_dict["assignment_type"] = "Team"

                if artifact_review.status == ArtifactReview.ArtifactReviewType.REOPEN:
                    artifact_review_dict["status"] = "REOPEN"
                else:
                    artifact_review_dict["status"] = (
                        "LATE"
                        if feedback_survey[0].date_due.astimezone(pytz.timezone("America/Los_Angeles")) < datetime.now().astimezone(pytz.timezone("America/Los_Angeles"))
                        else artifact_review.status
                    )

                artifact_review_dict["course_id"] = registration.course_id
                artifact_review_dict["course_number"] = course.course_number
                artifact_review_dict["assignment_id"] = assignment.id
                response_data.append(artifact_review_dict)

        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Unassign specific artifact review for a student",
        tags=["artifact_reviews"],
        responses={"204": openapi.Response(description="Successfully unassigned review.")},
    )
    def delete(self, request, course_id, assignment_id, *args, **kwargs):
        artifact_review_id = request.data.get("artifact_review_id")
        artifact_review = get_object_or_404(ArtifactReview, id=artifact_review_id)
        artifact_review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArtifactReviewersList(generics.GenericAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get all artifact reviews for an artifact",
        tags=["artifact_reviews"],
    )
    def get(self, request, course_id, assignment_id, artifact_id, *args, **kwargs):
        user_id = get_user_pk(request)
        # print('art', artifact_id)
        artifact = Artifact.objects.get(id=artifact_id)
        artifact_reviews = ArtifactReview.objects.filter(artifact=artifact)
        response_data = []
        for artifact_review in artifact_reviews:
            artifact_review_data = model_to_dict(artifact_review)
            registration = artifact_review.user
            reviewer = registration.user
            artifact_review_data["reviewer"] = reviewer.andrew_id
            artifact_review_data["pokable"] = True
            pokes = Notification.objects.filter(
                receiver=reviewer.id, sender=user_id, type=Notification.NotificationType.POKE
            )
            if len(pokes) > 0:
                latest_poke = max([poke.timestamp for poke in pokes])
                now = timezone.now()
                one_day = timedelta(days=1)
                time_diff = now - latest_poke
                if len(pokes) >= 3 or time_diff < one_day:
                    artifact_review_data["pokable"] = False
            response_data.append(artifact_review_data)
            # print('response', response_data)
        return Response(response_data)

# TO BE continue


class OptionalArtifactReview(generics.GenericAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get artifact reviews for a specific user",
        tags=["artifact_reviews"],
        responses={
            200: openapi.Schema(
                description="Artifact reviews for a user",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "artifact": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "user": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "status": openapi.Schema(type=openapi.TYPE_STRING, enum=["COMPLETED", "INCOMPLETE", "LATE"]),
                        "max_artifact_review_score": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "artifact_review_score": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "reviewing": openapi.Schema(type=openapi.TYPE_STRING),
                        "course_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "course_number": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "assignment_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        # get assignment, course and user from the request
        # (just record the completed reviews of one artifact)
        # and return the artifact with least number of completed reviews, and find the user related to that artifact
        # but it can not be the user himself, or those which already assigned to him
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)


class UserArtifactReviewList(generics.RetrieveAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get artifact reviews for a specific user",
        tags=["artifact_reviews"],
        responses={
            200: openapi.Schema(
                description="Artifact reviews for a user",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "artifact": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "user": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "status": openapi.Schema(type=openapi.TYPE_STRING, enum=["COMPLETED", "INCOMPLETE", "LATE"]),
                        "max_artifact_review_score": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "artifact_review_score": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "reviewing": openapi.Schema(type=openapi.TYPE_STRING),
                        "course_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "course_number": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "assignment_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        # assigning the reviews
        # get FeedbackSurvey and filter the ones that is_released is false and release_date is before now
        to_be_assigned_survey = FeedbackSurvey.objects.filter(is_released=False, date_released__lte=datetime.now())
        # find all the students in this course

        for survey in to_be_assigned_survey:
            if survey.is_released == True:
                continue

            survey.is_released = True
            survey.save()

            assignment = survey.assignment
            min_reviewer = assignment.min_reviewers
            course_id = assignment.course
            registrations = Registration.objects.filter(course_id=course_id, user__is_staff=False)

            # find all the artifacts for this assignment, and make sure they all are from distinct entities
            distinct_entity_ids = Artifact.objects.filter(
                assignment_id=assignment.id).values_list('entity_id', flat=True).distinct()
            artifacts = Artifact.objects.filter(entity_id__in=distinct_entity_ids)

            # number of uploader(= num of artifacts)
            uploader_num = len(artifacts)
            if uploader_num == 0:
                continue

            # number of registration (number of people in class)
            regis_num = len(registrations)
            if regis_num == 0:
                continue

            # number of reviews need to be assigned per registration member in course
            num_review_assigned_per_person = math.ceil((min_reviewer * uploader_num) / regis_num)
            # total number of reviews need to be assigned after calculation to satisfy conditions
            num_review_assigned = num_review_assigned_per_person * regis_num
            # number of uploader(artifact) that needs to be assigned for one additional time
            num_uploader_assigned_again = num_review_assigned % uploader_num
            # how many times each uploader(artifact) needs to be assigned to be reviewed
            num_assigned = num_review_assigned // uploader_num
            # print(num_review_assigned_per_person, num_review_assigned, num_uploader_assigned_again, num_assigned)

            # dict {key: uploader, val: artifact}
            uploader_artifact_list = {}
            for artifact in artifacts:
                # uploder = Membership.objects.get(entity=artifact.entity).student.user.name_or_andrew_id()
                uploader = artifact.entity.id
                uploader_artifact_list[uploader] = artifact

            # dict {key: registration_andrew_id(str), val: number of reviews assigned to the current user}
            registration_dict = {}
            for registration in registrations:
                membership = Membership.objects.filter(student=registration)
                for ele in membership:
                    print(ele.entity.id)
                    if ele.entity.id in distinct_entity_ids:
                        # registration_dict[ele.entity.id] = [0, registration]
                        registration_dict[registration.user.name_or_andrew_id()] = [0, registration, ele.entity.id]
                        break

            for uploader in uploader_artifact_list:
                cur_num_assigned = num_assigned
                if num_uploader_assigned_again > 0:
                    cur_num_assigned += 1
                    num_uploader_assigned_again -= 1
                for student in list(registration_dict.keys()):
                    if student[2] == uploader:
                        continue
                    if cur_num_assigned == 0:
                        break
                    registration_dict[student][0] += 1
                    # assign~!!
                    artifact_review = ArtifactReview(
                        artifact=uploader_artifact_list[uploader], user=registration_dict[student][1], status=ArtifactReview.ArtifactReviewType.INCOMPLETE)
                    artifact_review.save()

                    if registration_dict[student][0] >= num_review_assigned_per_person:
                        del registration_dict[student]
                    cur_num_assigned -= 1
                    if cur_num_assigned == 0:
                        break

        # original code
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        registrations = Registration.objects.filter(user=user)
        response_data = []
        for registration in registrations:
            artifact_reviews = ArtifactReview.objects.filter(user=registration)
            for artifact_review in artifact_reviews:
                artifact = get_object_or_404(Artifact, id=artifact_review.artifact_id)
                artifact_review_data = model_to_dict(artifact_review)
                assignment = get_object_or_404(Assignment, id=artifact.assignment_id)
                feedbackSurvey = get_object_or_404(FeedbackSurvey, assignment=assignment)
                if (
                    feedbackSurvey.date_released.astimezone(pytz.timezone(
                        "America/Los_Angeles")) > datetime.now().astimezone(pytz.timezone("America/Los_Angeles"))
                    or artifact_review.status == ArtifactReview.ArtifactReviewType.COMPLETED
                ):
                    continue
                if assignment.assignment_type == Assignment.AssigmentType.Individual:
                    artifact_review_data["reviewing"] = Membership.objects.get(
                        entity=artifact.entity
                    ).student.user.andrew_id
                    artifact_review_data["assignment_type"] = "Individual"
                else:
                    artifact_review_data["reviewing"] = artifact.entity.team.name
                    artifact_review_data["assignment_type"] = "Team"
                course = get_object_or_404(Course, id=registration.course_id)
                artifact_review_data["date_due"] = feedbackSurvey.date_due
                if artifact_review.status == ArtifactReview.ArtifactReviewType.REOPEN:
                    artifact_review_data["status"] = "REOPEN"
                else:
                    artifact_review_data["status"] = (
                        "LATE"
                        if feedbackSurvey.date_due.astimezone(pytz.timezone("America/Los_Angeles")) < datetime.now().astimezone(pytz.timezone("America/Los_Angeles"))
                        else artifact_review.status
                    )
                if artifact_review.status != ArtifactReview.ArtifactReviewType.COMPLETED:
                    print("status", feedbackSurvey.date_due.astimezone(pytz.timezone("America/Los_Angeles")),
                          " ", datetime.now().astimezone(pytz.timezone("America/Los_Angeles")))
                    if feedbackSurvey.date_due.astimezone(pytz.timezone("America/Los_Angeles")) < datetime.now().astimezone(pytz.timezone("America/Los_Angeles")):
                        artifact_review_data["status"] = ArtifactReview.ArtifactReviewType.LATE
                        artifact_review.status = ArtifactReview.ArtifactReviewType.LATE
                        artifact_review.save()
                    else:
                        artifact_review_data["status"] = artifact_review.status

                artifact_review_data["course_id"] = registration.course_id
                artifact_review_data["course_number"] = course.course_number
                artifact_review_data["assignment_id"] = assignment.id

                response_data.append(artifact_review_data)

        return Response(response_data, status=status.HTTP_200_OK)


class ArtifactReviewDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer

    @swagger_auto_schema(
        operation_description="Get artifact review details",
        tags=["artifact_reviews"],
        responses={
            200: openapi.Schema(
                description="Artifact review contents",
                type=openapi.TYPE_OBJECT,
                properties={
                    "pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "instructions": openapi.Schema(type=openapi.TYPE_STRING),
                    "artifact_pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                    **base_artifact_review_schema,
                },
            )
        },
    )
    def get(self, request, course_id, assignment_id, artifact_review_pk, *args, **kwargs):
        artifact_review = get_object_or_404(ArtifactReview, id=artifact_review_pk)
        artifact = artifact_review.artifact
        assignment = get_object_or_404(Assignment, id=assignment_id)
        survey_template = assignment.survey
        if not survey_template:
            return Response({"message": "Survey has not been created."}, status=status.HTTP_400_BAD_REQUEST)
        data = dict()
        data["pk"] = survey_template.pk
        data["name"] = survey_template.name
        data["artifact_pk"] = artifact.pk
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
                curr_question["question_type"] = question.question_type
                curr_question["phrased_positively"] = question.phrased_positively
                curr_question["gamified"] = question.gamified
                curr_question["min"] = question.min
                curr_question["max"] = question.max
                curr_question["answer"] = []
                answer_filter = {"artifact_review_id": artifact_review_pk, "option_choice__question": question}
                answers = (
                    Answer.objects.filter(**answer_filter)
                    if question.question_type != Question.QuestionType.SLIDEREVIEW
                    else ArtifactFeedback.objects.filter(**answer_filter)
                )

                for answer in answers:
                    curr_answer = dict()

                    curr_answer["page"] = (
                        answer.page if question.question_type == Question.QuestionType.SLIDEREVIEW else None
                    )

                    curr_answer["text"] = answer.answer_text
                    curr_question["answer"].append(curr_answer)
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
        operation_description="Update artifact review details",
        tags=["artifact_reviews"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "artifact_review_detail": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "question_pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "answer_text": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                )
            },
        ),
        responses={
            200: openapi.Schema(
                description="Artifact successfully updated",
                type=openapi.TYPE_OBJECT,
                properties={
                    "exp": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "level": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "next_level_exp": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "points": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
        },
    )
    def patch(self, request, course_id, assignment_id, artifact_review_pk, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        course = get_object_or_404(Course, id=course_id)
        registration = get_object_or_404(Registration, course=course, user=user)
        artifact_review_detail = request.data.get("artifact_review_detail")
        artifact_review = get_object_or_404(ArtifactReview, id=artifact_review_pk)

        # Add points and experience if not previously completed
        if artifact_review.status != ArtifactReview.ArtifactReviewType.COMPLETED:
            behavior = Behavior.objects.get(operation="survey")
            if artifact_review.status == ArtifactReview.ArtifactReviewType.OPTIONAL_INCOMPLETE:
                behavior = Behavior.objects.get(operation="optional_survey")
            elif artifact_review.status == ArtifactReview.ArtifactReviewType.LATE:
                behavior = Behavior.objects.get(operation="late")

            user.exp += behavior.points
            user.save()
            registration.points += behavior.points
            registration.course_experience += behavior.points
            registration.save()

        # Delete old answers
        Answer.objects.filter(artifact_review_id=artifact_review_pk).delete()
        grade = 0
        max_grade = 0
        for answer in artifact_review_detail:
            question_pk = answer["question_pk"]
            answer_text = answer["answer_text"]
            question = Question.objects.get(id=question_pk)
            question_type = question.question_type
            is_required = question.is_required
            if is_required and answer_text == "":
                return Response(
                    {"message": "Please answer all required questions."}, status=status.HTTP_400_BAD_REQUEST
                )
            if answer_text == "":
                continue
            option_choices = question.options.all()
            if (
                question_type == Question.QuestionType.MULTIPLECHOICE
                or question_type == Question.QuestionType.MULTIPLESELECT
            ):
                for option_choice in option_choices:
                    if option_choice.text == answer_text:
                        answer = Answer()
                        answer.option_choice = option_choice
                        answer.artifact_review = artifact_review
                        answer.answer_text = answer_text
                        answer.save()
                        break
            elif (
                question_type == Question.QuestionType.FIXEDTEXT
                or question_type == Question.QuestionType.MULTIPLETEXT
                or question_type == Question.QuestionType.TEXTAREA
                or question_type == Question.QuestionType.NUMBER
                or question_type == Question.QuestionType.SCALEMULTIPLECHOICE
            ):
                option_choice = option_choices[0]
                answer = Answer()
                answer.option_choice = option_choice
                answer.artifact_review = artifact_review
                answer.answer_text = answer_text
                answer.save()
            else:
                # question type: slide
                option_choice = option_choices[0]
                artifact_feedback = ArtifactFeedback()
                artifact_feedback.artifact_review = artifact_review

                artifact_feedback.option_choice = option_choice
                artifact_feedback.answer_text = answer_text
                page = answer["page"]

                artifact_feedback.page = page
                artifact_feedback.save()

        artifact_review.status = ArtifactReview.ArtifactReviewType.COMPLETED
        artifact_review.artifact_review_score = grade
        artifact_review.max_artifact_review_score = max_grade
        artifact_review.save()

        # update the number of completed reviews for this artifact
        artifact = get_object_or_404(Artifact, id=artifact_review.artifact_id)
        artifact.uploader_id = artifact.uploader_id + 1
        artifact.save()

        artifact = get_object_or_404(Artifact, id=artifact_review.artifact_id)
        assignment = get_object_or_404(Assignment, id=artifact.assignment_id)
        artifacts = Artifact.objects.filter(assignment_id=assignment).order_by('uploader_id')
        my_entity_list = Membership.objects.filter(student_id=registration).values_list('entity_id', flat=True)

        artifact_ids_assigned = ArtifactReview.objects.filter(user=registration).values_list('artifact_id', flat=True)
        artifact_ids_mine = []
        myself_artifact_id = None
        for my_entity in my_entity_list:
            tmp = Artifact.objects.filter(entity_id=my_entity)
            if len(tmp) != 0:
                myself_artifact_id = tmp[0].id
                artifact_ids_mine.append(myself_artifact_id)

        for a in artifacts:
            if a.id not in artifact_ids_assigned and a.id not in artifact_ids_mine:
                optional_artifact_review = ArtifactReview(
                    artifact=a, user=registration, status=ArtifactReview.ArtifactReviewType.OPTIONAL_INCOMPLETE)
                optional_artifact_review.save()
                break
                # assign review

        user = get_object_or_404(CustomUser, id=user_id)
        level = inv_level_func(user.exp)
        next_level_exp = level_func(level + 1)
        response_data = {
            "exp": user.exp,
            "level": level,
            "next_level_exp": next_level_exp,
            "points": registration.points,
            "course_experience": registration.course_experience,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ArtifactReviewIpsatization(generics.RetrieveAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get artifact review ipsatization",
        tags=["reports"],
    )
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        artifact_reviews = ArtifactReview.objects.filter(artifact__assignment_id=assignment_id)
        artifacts = Artifact.objects.filter(assignment_id=assignment_id)
        registrations = Registration.objects.filter(courses_id=course_id)
        # List of registration ids (row)
        registrations_id_list = [registration.id for registration in registrations]
        # List of artifact ids (column)
        artifacts_id_list = [artifact.id for artifact in artifacts]

        # 2d matrix of artifact_reviews by (registration_ids x artifact_ids)
        matrix = [[None for j in range(len(artifacts_id_list))] for i in range(len(registrations_id_list))]

        for artifact_review in artifact_reviews:
            artifact = artifact_review.artifact
            user = artifact_review.user
            if artifact_review.status == ArtifactReview.ArtifactReviewType.INCOMPLETE:
                continue
            # fill in the matrix with artifact_review_score / max_artifact_review_score
            matrix[registrations_id_list.index(user.id)][artifacts_id_list.index(artifact.id)] = (
                artifact_review.artifact_review_score / artifact_review.max_artifact_review_score
            )

        ipsatization_MAX = 100
        ipsatization_MIN = 80
        assignment = get_object_or_404(Assignment, id=assignment_id)
        # get ipsatization_MAX and ipsatization_MIN from assignment
        if assignment.ipsatization_max and assignment.ipsatization_min:
            ipsatization_MAX = assignment.ipsatization_max
            ipsatization_MIN = assignment.ipsatization_min

        if "ipsatization_MAX" in request.query_params and "ipsatization_MIN" in request.query_params:
            ipsatization_MAX = int(request.query_params["ipsatization_MAX"])
            ipsatization_MIN = int(request.query_params["ipsatization_MIN"])

        # calculate ipsatizated score at backend
        def ipsatization(data, ipsatization_MAX, ipsatization_MIN):
            def convert(score):
                # 0 <= score <= 1, convert to -1 to 1
                return (score - 0.5) * 2

            def min_max_scale(data):
                min_value = min(data)
                max_value = max(data)
                normalized_data = []
                for value in data:
                    normalized_value = (value - min_value) / (max_value - min_value)
                    normalized_data.append(normalized_value)
                return normalized_data

            # Calculate the mean and standard deviation of each survey
            means = data.mean(axis=1)
            stds = data.std(axis=1)
            # Perform ipsatization on the data
            i_data = data.copy()
            for i in range(len(data)):
                for j in range(len(data.columns)):
                    i_data.iloc[i, j] = (
                        (data.iloc[i, j] - means[i]) / stds[i] if stds[i] != 0 else convert(data.iloc[i, j])
                    )
            # Calculate the means of each survey as their score
            i_means = i_data.mean()
            # Normalize the scores
            normalized_means = min_max_scale(i_means)

            # Convert scores to desired range
            ipsatization_range = ipsatization_MAX - ipsatization_MIN
            final_means = [score * ipsatization_range + ipsatization_MIN for score in normalized_means]
            return final_means

        df = pd.DataFrame(matrix, columns=artifacts_id_list, dtype=float)
        # handle None value in matrix with mean value of each row
        m = df.mean(axis=1)
        for i, col in enumerate(df):
            df.iloc[:, i] = df.iloc[:, i].fillna(m)
        ipsatizated_data = ipsatization(df, ipsatization_MAX, ipsatization_MIN)
        # final result
        artifacts_id_and_scores_dict = dict(zip(artifacts_id_list, ipsatizated_data))
        # retrive entities with artifacts_id_list
        entities = []
        if assignment.assignment_type == "Individual":
            for artifact_id in artifacts_id_list:
                artifact = get_object_or_404(Artifact, id=artifact_id)
                entity = artifact.entity
                member = entity.members.first()
                first_and_last_name = member.first_name + " " + member.last_name
                entities.append(first_and_last_name)
        else:
            # Team assignment
            for artifact_id in artifacts_id_list:
                artifact = get_object_or_404(Artifact, id=artifact_id)
                entity = artifact.entity
                group_name = entity.team.name
                members = entity.members
                members_first_and_last_name = [member.first_name + " " + member.last_name for member in members]
                entities.append(group_name + " (" + ", ".join(members_first_and_last_name) + ")")

        content = {
            "artifacts_id_and_scores_dict": artifacts_id_and_scores_dict,
            "ipsatization_MAX": ipsatization_MAX,
            "ipsatization_MIN": ipsatization_MIN,
            "assignment_type": assignment.assignment_type,
            "entities": entities,
        }
        return Response(content, status=status.HTTP_200_OK)


class ArtifactReviewStatus(generics.UpdateAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Patch artifact review status",
        tags=["artifact_reviews"],
    )
    def patch(self, request, course_id, assignment_id, artifact_review_pk, *args, **kwargs):
        artifact_review = ArtifactReview.objects.get(id=artifact_review_pk)
        artifact_status = request.data.get("status")
        available_statuses = [
            ArtifactReview.ArtifactReviewType.COMPLETED,
            ArtifactReview.ArtifactReviewType.INCOMPLETE,
            ArtifactReview.ArtifactReviewType.REOPEN,
        ]
        if artifact_status not in available_statuses:
            return Response({"message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        artifact_review.status = artifact_status
        artifact_review.save()
        return Response({"message": "Status updated"}, status=status.HTTP_200_OK)
