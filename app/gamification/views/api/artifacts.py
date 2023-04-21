from wsgiref.util import FileWrapper
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from app.gamification.models.assignment import Assignment
from app.gamification.models.course import Course
from app.gamification.models.entity import Individual, Team
from app.gamification.models.membership import Membership
from app.gamification.models.user import CustomUser
from app.gamification.utils import get_user_pk
from app.gamification.models.artifact import Artifact
from app.gamification.models.artifact_review import ArtifactReview
from app.gamification.models.registration import Registration
from app.gamification.serializers.answer import ArtifactReviewSerializer
import pytz
from datetime import datetime
from django.conf import settings
from app.gamification.utils import generate_presigned_url, generate_presigned_post

class SubmitArtifact(generics.ListCreateAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    permission_classes = [permissions.AllowAny]

    def create_artifact(self, request, assignment, registration, entity):
        try:
            artifact = Artifact.objects.get(
                assignment=assignment, entity=entity)
        except Artifact.DoesNotExist:
            artifact = Artifact()
        artifact.assignment = assignment
        artifact.upload_time = datetime.now().astimezone(
            pytz.timezone('America/Los_Angeles'))
        key = request.FILES.get('artifact')
        # Save the object key to the database
        if settings.USE_S3:
            key = f'assignment_files/artifact_{assignment.id}_{entity.id}.pdf'
        artifact.file = key
        artifact.entity = entity
        artifact.save()

        return artifact

    def create_artifact_review(self, artifact, registration, course, assignment_type, entity):
        if assignment_type == 'Team':
            team_members = [i.pk for i in entity.members]
            registrations = [i for i in Registration.objects.filter(
                courses=course) if i.users.pk not in team_members]
            for registration in registrations:
                if registration.userRole == Registration.UserRole.Student:
                    artifact_review = ArtifactReview(
                        artifact=artifact, user=registration)
                    artifact_review.save()
        else:
            registrations = [i for i in Registration.objects.filter(
                courses=course) if i.id != registration.id]
            if registration.userRole == Registration.UserRole.Student:
                for single_registration in registrations:
                    artifact_review = ArtifactReview(
                        artifact=artifact, user=single_registration)
                    artifact_review.save()

    def post(self, request, course_id, assignment_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, pk=user_id)
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        course = get_object_or_404(Course, pk=course_id)
        registration = Registration.objects.get(users=user, courses=course)
        assignment_type = assignment.assignment_type
        if assignment_type == "Individual":
            try:
                entity = Individual.objects.get(
                    registration=registration, course=course)
            except Individual.DoesNotExist:
                individual = Individual(course=course)
                individual.save()
                membership = Membership(
                    student=registration, entity=individual)
                membership.save()
                entity = Individual.objects.get(
                    registration=registration, course=course)
        elif assignment_type == "Team":
            try:
                entity = Team.objects.get(
                    registration=registration, course=course)
            except Team.DoesNotExist:
                return Response({"messages": "No team found"}, status=status.HTTP_404_NOT_FOUND)

        artifact = self.create_artifact(
            request, assignment, registration, entity)
        
        # Generate the presigned URL to share with the user.
        key = artifact.file.name
        if settings.USE_S3:
            upload_url = generate_presigned_post(key)
            download_url = generate_presigned_url(key, http_method='GET')
        else:
            upload_url = f'http://{settings.ALLOWED_HOSTS[1]}:8000{artifact.file.url}'
            download_url = f'http://{settings.ALLOWED_HOSTS[1]}:8000{artifact.file.url}'
        self.create_artifact_review(
            artifact, registration, course, assignment_type, entity)
        
        return Response({
            'upload_url': upload_url,
            'download_url': download_url
        }, status=status.HTTP_201_CREATED)

    def get(self, request, course_id, assignment_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, pk=user_id)
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        if assignment.assignment_type == "Individual":
            entity = Individual.objects.get(
                registration__users=user, course__id=course_id)
        elif assignment.assignment_type == "Team":
            entity = Team.objects.get(
                registration__users=user, course__id=course_id)

        try:
            artifact = Artifact.objects.get(
                assignment=assignment, entity=entity)
        except Artifact.DoesNotExist:
            return Response({"messages": "No submission"}, status=status.HTTP_404_NOT_FOUND)
        data = dict()
        data['create_date'] = artifact.upload_time
        # get an open file handle (I'm just using a file attached to the model for this example):
        key = artifact.file.name
        path = f'http://{settings.ALLOWED_HOSTS[1]}:8000{artifact.file.url}'
        
        if settings.USE_S3:
            path = generate_presigned_url(key, http_method='GET')
        data['file_path'] = path
    
        data['artifact_pk'] = artifact.pk
        return Response(data, status=status.HTTP_200_OK)


class GetArtifact (generics.RetrieveAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, course_id, assignment_id, artifact_id, *args, **kwargs):
        artifact = get_object_or_404(Artifact, pk=artifact_id)
        data = dict()
        data['create_date'] = artifact.upload_time

        key = artifact.file.name
        path = f'http://{settings.ALLOWED_HOSTS[1]}:8000{artifact.file.url}'
        
        if settings.USE_S3:
            path = generate_presigned_url(key, http_method='GET')
        data['file_path'] = path
    
        
        return Response(data, status=status.HTTP_200_OK)
