from datetime import datetime

import pytz
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models.artifact import Artifact
from app.gamification.models.artifact_review import ArtifactReview
from app.gamification.models.assignment import Assignment
from app.gamification.models.behavior import Behavior
from app.gamification.models.course import Course
from app.gamification.models.entity import Individual, Team
from app.gamification.models.membership import Membership
from app.gamification.models.registration import Registration
from app.gamification.models.user import CustomUser
from app.gamification.serializers.answer import ArtifactReviewSerializer
from app.gamification.utils.auth import get_user_pk
from app.gamification.utils.levels import inv_level_func, level_func
from app.gamification.utils.s3 import generate_presigned_post, generate_presigned_url


class AssignmentArtifact(generics.ListCreateAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    permission_classes = [permissions.AllowAny]

    def create_artifact(self, request, assignment, registration, entity):
        print("create artifact", registration)
        try:
            artifact = Artifact.objects.get(assignment=assignment, entity=entity)
        except Artifact.DoesNotExist:
            artifact = Artifact()
        artifact.assignment = assignment
        artifact.upload_time = datetime.now().astimezone(pytz.timezone("America/Los_Angeles"))
        key = request.FILES.get("artifact")
        # Save the object key to the database
        if settings.USE_S3:
            key = f"assignment_files/artifact_{assignment.id}_{entity.id}.pdf"
        artifact.file = key
        artifact.entity = entity
        artifact.uploader = registration
        artifact.save()

        return artifact
    
    def next_classmate(self, user_index, classmates):
        if user_index == len(classmates) - 1:
            if classmates[0].user.is_staff:
                return self.next_classmate(0, classmates)
            return classmates[0]
        else:
            if classmates[user_index + 1].user.is_staff:
                return self.next_classmate(user_index + 1, classmates)
            return classmates[user_index + 1]

    def create_artifact_review(self, artifact, user, course, assignment_type, entity):
        if assignment_type == Assignment.AssigmentType.Team:
            team_members = [i.pk for i in entity.members]
            registrations = [i for i in Registration.objects.filter(course=course) if i.user.pk not in team_members]
            for registration in registrations:
                user = registration.user
                if not user.is_staff:
                    # create artifact review if it doesn't exist
                    if not ArtifactReview.objects.filter(artifact=artifact, user=registration).exists():
                        artifact_review = ArtifactReview(artifact=artifact, user=registration)
                        artifact_review.save()
        else:
            classmates = Registration.objects.filter(course=course)
            if not user.is_staff:
                for i in range(len(classmates)):
                    if classmates[i].user == user:
                        next_one = self.next_classmate(i, classmates)
                        if not ArtifactReview.objects.filter(artifact=artifact, user=next_one).exists():
                            print("create artifact review ", next_one)
                            artifact_review = ArtifactReview(artifact=artifact, user=next_one)
                            artifact_review.save()
                        
            
            # registrations = [i for i in Registration.objects.filter(course=course) if i.user != user]
            # if not user.is_staff:
            #     for single_registration in registrations:
            #         print("create artifact review ", single_registration)
            #         single_user = single_registration.user
            #         # create artifact review if it doesn't exist
            #         if (
            #             not ArtifactReview.objects.filter(artifact=artifact, user=single_registration).exists()
            #             and not single_user.is_staff
            #         ):
            #             artifact_review = ArtifactReview(artifact=artifact, user=single_registration)
            #             artifact_review.save()

    @swagger_auto_schema(
        operation_description="Upload an artifact for an assignment",
        tags=["artifacts"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "artifact": openapi.Schema(type=openapi.TYPE_FILE),
            },
        ),
        responses={
            201: openapi.Schema(
                description="Artifact uploaded",
                type=openapi.TYPE_OBJECT,
                properties={
                    "upload_url": openapi.Schema(type=openapi.TYPE_STRING),
                    "download_url": openapi.Schema(type=openapi.TYPE_STRING),
                    "exp": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "level": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "next_level_exp": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "points": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
            404: openapi.Response(
                description="No team found",
            ),
        },
    )
    def post(self, request, course_id, assignment_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, pk=user_id)
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        course = get_object_or_404(Course, pk=course_id)
        registration = Registration.objects.get(user=user, course=course)
        assignment_type = assignment.assignment_type
        if assignment_type == "Individual":
            try:
                entity = Individual.objects.get(registration=registration, course=course)
            except Individual.DoesNotExist:
                individual = Individual(course=course)
                individual.save()
                membership = Membership(student=registration, entity=individual)
                membership.save()
                entity = Individual.objects.get(registration=registration, course=course)
        elif assignment_type == "Team":
            try:
                entity = Team.objects.get(registration=registration, course=course)
            except Team.DoesNotExist:
                return Response({"message": "No team found"}, status=status.HTTP_404_NOT_FOUND)

        # Add user experience and registration points if artifact is new
        artifact = Artifact.objects.filter(assignment=assignment, entity=entity)
        if not artifact.exists():
            try:
                behavior = Behavior.objects.get(operation="assignment")
                registration.points += behavior.points
                registration.course_experience += behavior.points
                registration.save()
                user.exp += behavior.points
                user.save()
            except Behavior.DoesNotExist:
                user.save()

        artifact = self.create_artifact(request, assignment, registration, entity)

        # Generate the presigned URL to share with the user.
        key = artifact.file.name
        if settings.USE_S3:
            upload_url = generate_presigned_post(key)
            download_url = generate_presigned_url(key, http_method="GET")
        else:
            upload_url = f"http://{settings.ALLOWED_HOSTS[2]}:8000{artifact.file.url}"
            download_url = f"http://{settings.ALLOWED_HOSTS[2]}:8000{artifact.file.url}"

        self.create_artifact_review(artifact, user, course, assignment_type, entity)
        level = inv_level_func(user.exp)
        next_level_exp = level_func(level + 1)

        return Response(
            {
                "upload_url": upload_url,
                "download_url": download_url,
                "exp": user.exp,
                "level": level,
                "next_level_exp": next_level_exp,
                "points": registration.points,
                "course_experience": registration.course_experience,
            },
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_description="Get artifact for an assignment",
        tags=["artifacts"],
        responses={
            200: openapi.Schema(
                description="Successfully obtained artifact",
                type=openapi.TYPE_OBJECT,
                properties={
                    "create_date": openapi.Schema(type=openapi.TYPE_STRING),
                    "file_path": openapi.Schema(type=openapi.TYPE_STRING),
                    "artifact_pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
            404: openapi.Response(
                description="No submission found",
            ),
        },
    )
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, pk=user_id)
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        if assignment.assignment_type == Assignment.AssigmentType.Individual:
            entity = Individual.objects.get(registration__user=user, course__id=course_id)
        elif assignment.assignment_type == Assignment.AssigmentType.Team:
            entity = Team.objects.get(registration__user=user, course__id=course_id)
        try:
            artifact = Artifact.objects.get(assignment=assignment, entity=entity)
        except Artifact.DoesNotExist:
            return Response({"message": "No submission"}, status=status.HTTP_404_NOT_FOUND)
        data = dict()
        data["create_date"] = artifact.upload_time
        key = artifact.file.name
        path = f"http://{settings.ALLOWED_HOSTS[2]}:8000{artifact.file.url}"

        if settings.USE_S3:
            path = generate_presigned_url(key, http_method="GET")
        data["file_path"] = path

        data["artifact_pk"] = artifact.pk
        return Response(data, status=status.HTTP_200_OK)


class ArtifactDetail(generics.RetrieveAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get artifact for an assignment by artifact id",
        tags=["artifacts"],
        responses={
            200: openapi.Schema(
                description="Successfully obtained artifact",
                type=openapi.TYPE_OBJECT,
                properties={
                    "create_date": openapi.Schema(type=openapi.TYPE_STRING),
                    "file_path": openapi.Schema(type=openapi.TYPE_STRING),
                    "artifact_pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
            404: openapi.Response(
                description="No submission found",
            ),
        },
    )
    def get(self, request, course_id, assignment_id, artifact_id, *args, **kwargs):
        artifact = get_object_or_404(Artifact, pk=artifact_id)
        data = dict()
        data["create_date"] = artifact.upload_time

        key = artifact.file.name
        path = f"http://{settings.ALLOWED_HOSTS[2]}:8000{artifact.file.url}"

        if settings.USE_S3:
            path = generate_presigned_url(key, http_method="GET")
        data["artifact_pk"] = artifact_id
        data["file_path"] = path

        return Response(data, status=status.HTTP_200_OK)
