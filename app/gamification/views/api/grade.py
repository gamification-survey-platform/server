from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from app.gamification import serializers
import json
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from app.gamification.utils import get_user_pk

from app.gamification.serializers import CourseSerializer, AssignmentSerializer, GradeSerializer
from django.shortcuts import get_object_or_404
from app.gamification.models import Assignment, Course, Registration, Team, Membership, Artifact, Individual, FeedbackSurvey, CustomUser, Grade
import pytz
from pytz import timezone
from datetime import datetime
from django.utils.timezone import now

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
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
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

            try:
                # get grade with artifact_id
                grade = Grade.objects.get(artifact=artifact)
            except Grade.DoesNotExist:
                return Response("Grade does not exist", status=status.HTTP_404_NOT_FOUND)
            
            context = {'grade_id': grade.pk,
                       'grade_title': grade.grade_title,
                       'score': grade.score,
                       'curved_score': grade.curved_score,
                       'timestamp': grade.timestamp,
                       'deduction': get_deductions_with_grade(grade)
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            def get_deductions_with_grade(grade):
                deductions = []
                for deduction in grade.deductions.all():
                    deductions.append(model_to_dict(deduction))
                return deductions
            
            # get artifact by assignment, and get grade by artifact
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            grades = Grade.objects.filter(artifact__assignment=assignment)
            # and retrive all deductions for each grade
            context = []
            for grade in grades:
                context.append({'grade_id': grade.pk,
                                'grade_title': grade.grade_title,
                                'score': grade.score,
                                'curved_score': grade.curved_score,
                                'timestamp': grade.timestamp,
                                'deduction': get_deductions_with_grade(grade)
                })
            return Response(context, status=status.HTTP_200_OK)
            # serializer = GradeSerializer(grades, many=True)
            # return Response(serializer.data)

            
    def post(self, request, course_id, assignment_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        userRole = Registration.objects.get(users=user, courses=course).userRole
        # if artifact_id in request.data:
        if 'artifact_id' in request.data:
            artifact_id = request.data.get('artifact_id')
            score = request.data.get('score')
            grade_title = request.data.get('grade_title')
            artifact = get_object_or_404(Artifact, pk=artifact_id)
            
            if userRole == Registration.UserRole.Instructor:
                # if grade already exists, update it (restful: usually we should use patch/put instead of post)
                data = None
                try:
                    grade = Grade.objects.get(artifact=artifact)
                    grade.score = score
                    grade.grade_title = grade_title
                except Grade.DoesNotExist:
                    grade = Grade.objects.create(artifact=artifact, score=score, grade_title=grade_title)
                
                grade.save()
                data = model_to_dict(grade)
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            # manage grades for all artifacts in an assignment
            # upgrade 'grade' in Grade table
            # e.g.: {1:80, 2:90, 3:100} ({id:score})
            artifacts_id_and_scores_dict = request.data.get('artifacts_id_and_scores_dict')
            grades = []
            for artifact_id, score in artifacts_id_and_scores_dict.items():
                artifact_id = int(artifact_id)
                grade = Grade.objects.get(artifact_id=artifact_id)
                grade.score = score
                grade.save()
                grades.append(model_to_dict(grade))
            
            return Response(grades, status=status.HTTP_200_OK)