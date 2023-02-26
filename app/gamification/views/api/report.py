from django.http import HttpResponse
from app.gamification import serializers
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from django.contrib import messages
from app.gamification.serializers import EntitySerializer
from django.shortcuts import get_object_or_404
from app.gamification.models import Assignment, Course, CustomUser, Registration, Team, Membership, Artifact, ArtifactReview, Entity, Team, Individual
import pytz
import json
from pytz import timezone
from datetime import datetime


class IsAdminOrReadOnly(permissions.BasePermission):
    '''
    Custom permission to only allow users to view read-only information.
    Admin users are allowed to view and edit information.
    '''

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

class ViewReport(generics.ListCreateAPIView):
    # queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        if 'andrew_id' in request.query_params:
            andrew_id = request.query_params['andrew_id']
            user = get_object_or_404(CustomUser, andrew_id=andrew_id)
            course = get_object_or_404(Course, pk=course_id)
            registration = get_object_or_404(
                Registration, users=user, courses=course)
            userRole = registration.userRole
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            assignment_type = assignment.assignment_type
            if assignment_type == "Individual":
                try:
                    entity = Individual.objects.get(
                        registration=registration, course=course)
                    team_name = str(andrew_id)
                except Individual.DoesNotExist:
                    # Create an Individual entity for the user
                    individual = Individual(course=course)
                    individual.save()
                    membership = Membership(student=registration, entity=individual)
                    membership.save()
                    entity = Individual.objects.get(
                        registration=registration, course=course)
                    team_name = str(andrew_id)
            elif assignment_type == "Team":
                try:
                    entity = Team.objects.get(registration=registration, course=course)
                    team_name = entity.name
                except Team.DoesNotExist:
                    # Alert: you need to be a member of the team to upload the artifact, forbidden
                    return Response("You are not a member of the team", status=status.HTTP_403_FORBIDDEN)
            else:
                return Response("Assignment type is not valid", status=status.HTTP_400_BAD_REQUEST)
            # find artifact id with assignment id and entity id
            # artifact = get_object_or_404(Artifact, assignment=assignment, entity=entity)
            try:
                artifact = Artifact.objects.get(assignment=assignment, entity=entity)
                artifact_exists_flag = True
                artifact_id = artifact.pk
                artifact_path = artifact.file.url
                artifact_url = r"/api/artifacts/" + str(artifact_id) + "/"
                artifact_answers_url = r"/api/artifacts/" + str(artifact_id) + r"/answers/statistics"
            except Artifact.DoesNotExist:
                print("artifact does not exist")
                artifact_exists_flag = False
                artifact_id = None
                artifact_path = None
                artifact_url = None
                artifact_answers_url = None
            context = {'user': user,
                    'course': course,
                    'entity': entity,
                    'userRole': userRole,
                    'artifact_url': artifact_url,
                    'artifact_path': artifact_path,
                    'team_name': team_name,
                    "artifact_exists_flag": artifact_exists_flag,
                    "artifact_answers_url": artifact_answers_url
                    }
            data = json.dumps(context)
            return Response(data)
        else:
            # missing andrew_id
            return Response("Missing andrew_id", status=status.HTTP_400_BAD_REQUEST)