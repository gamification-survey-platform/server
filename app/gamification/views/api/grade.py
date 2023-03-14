from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from app.gamification import serializers
import json
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from app.gamification.utils import get_user_pk

from app.gamification.serializers import CourseSerializer, AssignmentSerializer
from django.shortcuts import get_object_or_404
from app.gamification.models import Assignment, Course, Registration, Team, Membership, Artifact, Individual, FeedbackSurvey, CustomUser, Grade
import pytz
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

class GradeList(generics.ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        if 'andrew_id' in request.query_params:
            def get_deductions_with_grade(grade):
                deductions = []
                for deduction in grade.deductions.all():
                    deductions.append(model_to_dict(deduction))
                return deductions
            
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
            try:
                artifact = Artifact.objects.get(assignment=assignment, entity=entity)
                artifact_id = artifact.pk
            except Artifact.DoesNotExist:
                # TODO: we might need an 'Artifact' placeholder for all students after we create an assignment, 
                # cause sometimes we don't have to upload an artifact for an assignment (e.g. final exam presentation without slides or video)
                return Response("Artifact does not exist", status=status.HTTP_404_NOT_FOUND)
                
            # get grade with artifact_id
            grade = get_object_or_404(Grade, artifact=artifact)
            
            context = {'score': grade.score,
                       'timestamp': grade.timestamp,
                       'deduction': get_deductions_with_grade(grade)
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            # TODO: return all grades for a course
            return Response("Andrew ID is required", status=status.HTTP_400_BAD_REQUEST)
            
            
            