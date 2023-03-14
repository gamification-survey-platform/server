from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from app.gamification import serializers
import json
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from app.gamification.utils import get_user_pk

from app.gamification.serializers import DeductionSerializer
from django.shortcuts import get_object_or_404
from app.gamification.models import Assignment, Course, Registration, Team, Membership, Artifact, Individual, FeedbackSurvey, CustomUser, Grade, Deduction
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

class DeductionList(generics.ListCreateAPIView):
    queryset = Deduction.objects.all()
    serializer_class = DeductionSerializer
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, course_id, assignment_id, grade_id, *args, **kwargs):
        def get_deductions_with_grade(grade):
                deductions = []
                for deduction in grade.deductions.all():
                    deductions.append(model_to_dict(deduction))
                return deductions
        try:
            grade = Grade.objects.get(pk=grade_id)
        except Grade.DoesNotExist:
            return Response('Grade does not exist', status=status.HTTP_404_NOT_FOUND)
        context = {'deduction': get_deductions_with_grade(grade)}
        return Response(context, status=status.HTTP_200_OK)
            
    def post(self, request, course_id, assignment_id, grade_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        userRole = Registration.objects.get(users=user, courses=course).userRole
        
        grade = get_object_or_404(Grade, pk=grade_id)
        deduction_score = request.data['deduction_score']
        title = request.data['title']
        description = request.data['description']
        if userRole == Registration.UserRole.Instructor:
            deduction = Deduction.objects.create(grade=grade, deduction_score=deduction_score, title=title, description=description)
            deduction.save()
            data = model_to_dict(deduction)
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            

class DeductionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deduction.objects.all()
    serializer_class = DeductionSerializer
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, course_id, assignment_id, grade_id, deduction_id, *args, **kwargs):
        deduction = get_object_or_404(Deduction, pk=deduction_id)
        
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        userRole = Registration.objects.get(users=user, courses=course).userRole
        
        data = model_to_dict(deduction)
        data['user_role'] = userRole
        return Response(data, status=status.HTTP_200_OK)
    
    def patch(self, request, course_id, assignment_id, grade_id, deduction_id,  *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        userRole = Registration.objects.get(users=user, courses=course).userRole
        
        deduction = get_object_or_404(Deduction, pk=deduction_id)
        
        deduction_score = request.data['deduction_score']
        title = request.data['title']
        description = request.data['description']
        
        if userRole == Registration.UserRole.Instructor:
            try:
                deduction = Deduction.objects.get(pk=deduction_id)
            except Deduction.DoesNotExist:
                deduction = Deduction()
            deduction.deduction_score = deduction_score
            deduction.title = title
            deduction.description = description
            deduction.save()
            data = model_to_dict(deduction)
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
