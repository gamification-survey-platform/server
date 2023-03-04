from django.http import HttpResponse
from app.gamification import serializers
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from django.contrib import messages
from app.gamification.serializers import EntitySerializer, UserSerializer, CourseSerializer
from django.shortcuts import get_object_or_404
from app.gamification.models import Assignment, Course, CustomUser, Registration, Team, Membership, Artifact, ArtifactReview, Entity, Team, Individual
import pytz
import json
from pytz import timezone
from datetime import datetime
from app.gamification.utils import get_user_pk

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
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        if 'andrew_id' in request.query_params:
            # individual report
            andrew_id = request.query_params['andrew_id']
            user = get_object_or_404(CustomUser, andrew_id=andrew_id)
            course = get_object_or_404(Course, pk=course_id)
            registration = get_object_or_404(
                Registration, users=user, courses=course)
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            assignment_type = assignment.assignment_type
            
            if assignment_type == "Individual":
                entity = Individual.objects.get(
                    registration=registration, course=course)
                team_name = str(andrew_id)
            elif assignment_type == "Team":
                entity = Team.objects.get(registration=registration, course=course)
                team_name = entity.name

            artifact_id = None
            artifact_url = None
            artifact_answers_url = None
            try:
                artifact = Artifact.objects.get(assignment=assignment, entity=entity)
                artifact_id = artifact.pk
                artifact_url = r"/api/artifacts/" + str(artifact_id) + "/"
                artifact_answers_url = r"/api/artifacts/" + str(artifact_id) + r"/answers/statistics"
            except Artifact.DoesNotExist:
                return Response("Artifact does not exist", status=status.HTTP_404_NOT_FOUND)

            context = {'andrew_id': user.andrew_id,
                    'course_name': course.course_name,
                    'team_name': team_name,
                    'artifact_url': artifact_url, # api to retrive artifact url
                    "artifact_answers_url": artifact_answers_url # api to retrive answers url
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            # assignment report
            course = get_object_or_404(Course, pk=course_id)
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            assignment_type = assignment.assignment_type
            user_id = get_user_pk(request)
            user = get_object_or_404(CustomUser, id=user_id)
            userRole = Registration.objects.get(users=user, courses=course).userRole
            students = []
            teams = []
            if assignment_type == "Individual":
                registrations = Registration.objects.filter(courses=course_id, userRole = Registration.UserRole.Student)
                counter = 0
                student_row = []
                for registration in registrations:
                    student_row.append(registration.users.andrew_id)
                    counter += 1
                    if counter == 4:
                        students.append(student_row)
                        counter = 0
                        student_row = []
                students.append(student_row)
                    
            elif assignment_type == "Team":
                all_teams = Team.objects.filter(course = course)
                team_row = []
                counter = 0
                for team in all_teams:
                    team_row.append(team.name)
                    counter += 1
                    if counter == 4:
                        teams.append(team_row)
                        counter = 0
                        team_row = []
                teams.append(team_row)
            
            # students or teams is an empty list
            context = {
                'userRole': userRole,
                'students': students,
                'teams': teams
            }
            return Response(context, status=status.HTTP_200_OK)
            
