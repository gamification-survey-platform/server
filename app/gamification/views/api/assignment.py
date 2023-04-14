from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from app.gamification import serializers
import json
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from app.gamification.utils import get_user_pk

from app.gamification.serializers import CourseSerializer, AssignmentSerializer
from django.shortcuts import get_object_or_404
from app.gamification.models import Assignment, Course, Registration, Team, Membership, Artifact, Individual, FeedbackSurvey, CustomUser
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

class AssignmentList(generics.ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.AllowAny] # [permissions.IsAuthenticated]

    def get(self, request, course_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        user_role = Registration.objects.get(users=user, courses=course_id).userRole
        course = get_object_or_404(Course, pk=course_id)
        assignments = Assignment.objects.filter(course=course)
        assignments = [model_to_dict(assignment) for assignment in assignments]
        for assignment in assignments:
            assignment['user_role'] = user_role
        return Response(assignments, status=status.HTTP_200_OK)

    def post(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        userRole = Registration.objects.get(users=user, courses=course).userRole
        assignment_name = request.data.get('assignment_name')
        assignment_type = request.data.get('assignment_type')
        date_released = request.data.get('date_released')
        date_due = request.data.get('date_due')
        description = request.data.get('description')
        submission_type = request.data.get('submission_type')
        total_score = request.data.get('total_score')
        weight = request.data.get('weight')
        review_assign_policy = request.data.get('review_assign_policy')
        if userRole == Registration.UserRole.Instructor:
            assignment = Assignment.objects.create(course=course, assignment_name=assignment_name, 
                                                   assignment_type=assignment_type, 
                                                   date_released=date_released, date_due=date_due, 
                                                   description=description, submission_type=submission_type, 
                                                   total_score=total_score, weight=weight, 
                                                   review_assign_policy=review_assign_policy)
            assignment.save()
            data = model_to_dict(assignment)
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class AssignmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, course_id, assignment_id,  *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        userRole = Registration.objects.get(users=user, courses=course).userRole
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        data = model_to_dict(assignment)
        data['user_role'] = userRole
        return Response(data, status=status.HTTP_200_OK)
    
    def patch(self, request, course_id, assignment_id,  *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        userRole = Registration.objects.get(users=user, courses=course).userRole
        assignment_name = request.data.get('assignment_name')
        assignment_type = request.data.get('assignment_type')
        date_due = request.data.get('date_due')
        date_released = request.data.get('date_released')
        description = request.data.get('description')
        submission_type = request.data.get('submission_type')
        total_score = request.data.get('total_score')
        weight = request.data.get('weight')
        review_assign_policy = request.data.get('review_assign_policy')
        if userRole == Registration.UserRole.Instructor:
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
        
    def delete(self, request, course_id, assignment_id,  *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        if user.is_staff or Registration.objects.get(users=user, courses=course).userRole == Registration.UserRole.Instructor:
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            assignment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


    
# class AssignmentList(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Assignment.objects.all()
#     serializer_class = AssignmentSerializer
#     permission_classes = [permissions.AllowAny] # [permissions.IsAuthenticated]
    
#     def get(self, request, course_id, *args, **kwargs):
#         course = get_object_or_404(Course, pk=course_id)
#         user_id = get_user_pk(request)
#         user = get_object_or_404(CustomUser, id=user_id)
#         userRole = Registration.objects.get(users=user, courses=course).userRole
        
#         if 'assignment_id' in request.query_params:
#             assignment_id = request.query_params['assignment_id']
#             if userRole == Registration.UserRole.Student:
#                 assignment = get_object_or_404(Assignment, pk=assignment_id)
#                 registration = get_object_or_404(
#                     Registration, users=user, courses=course_id)
#                 assignment_type = assignment.assignment_type   
                
#                 if assignment_type == "Individual":
#                     try:
#                         entity = Individual.objects.get(
#                             registration=registration, course=course)
#                     except Individual.DoesNotExist:
#                         # Create an Individual entity for the user
#                         individual = Individual(course=course)
#                         individual.save()
#                         membership = Membership(student=registration, entity=individual)
#                         membership.save()
#                         entity = Individual.objects.get(
#                             registration=registration, course=course)
#                 elif assignment_type == "Team":
#                     try:
#                         entity = Team.objects.get(registration=registration, course=course)
#                     except Team.DoesNotExist:
#                         # TODO: Alert: you need to be a member of the team to upload the artifact
#                         print("you need to be a member of the team to upload the artifact")
#                         return Response(status=status.HTTP_403_FORBIDDEN)
#                 else:
#                     # forbidden
#                     return Response(status=status.HTTP_401_UNAUTHORIZED)

#                 try:
#                     artifacts = Artifact.objects.filter(
#                         assignment=assignment, entity=entity)
#                     latest_artifact = artifacts.latest('upload_time')
#                     artifact_id = latest_artifact.id
#                 except Artifact.DoesNotExist:
#                     latest_artifact = "None"
#                     artifact_id = None

#                 # if artifact exist
#                 if artifact_id != None:
#                     latest_artifact_filename = latest_artifact.file.name.split('/')[-1]
#                 else:
#                     latest_artifact_filename = ""
#                 # return info with assignment and artifact
#                 info = {'user_role':userRole,'assignment': model_to_dict(assignment)}

#                 return Response(info)
#                 # return HttpResponse(info, content_type="application/json")
#             elif userRole == Registration.UserRole.Instructor or userRole == Registration.UserRole.TA:
#                 assignment = get_object_or_404(Assignment, pk=assignment_id)
#                 # Response for admin
#                 serializer = AssignmentSerializer(assignment)
#                 return Response({"user_role": userRole, "assignment":serializer.data})
#             else:
#                 # user role not found
#                 return Response(status=status.HTTP_401_UNAUTHORIZED)
#         else:
#             if userRole == Registration.UserRole.Student:
#                 infos = Assignment.objects.filter(course=course)
#                 user_is_individual = True
#                 try:
#                     registration = get_object_or_404(
#                         Registration, users=user, courses=course_id)
#                     entity = Team.objects.get(
#                         registration=registration, course=course)
#                     user_is_individual = False
#                 except Team.DoesNotExist:
#                     user_is_individual = True
#                 assignments = []
#                 for assignment in infos:
#                     assignment_type = assignment.assignment_type
#                     if assignment_type == 'Team' and user_is_individual:
#                         print('individual user can not see this assignment')
#                     else:
#                         if assignment.date_released != None and assignment.date_released.astimezone(pytz.timezone('America/Los_Angeles')) <= datetime.now().astimezone(
#                                 pytz.timezone('America/Los_Angeles')):
#                             assignments.append(assignment)
#                         elif assignment.date_released == None:
#                             assignments.append(assignment)
#                 assignments_info = []
#                 for a in assignments:
#                     feedback_survey = FeedbackSurvey.objects.filter(assignment=a)
#                     assign = dict()
#                     assign = model_to_dict(a)
#                     assign['feedback_survey'] = feedback_survey.count()
#                     if feedback_survey.count() == 1:
#                         feedback_survey_release_date = feedback_survey[0].date_released.astimezone(
#                             pytz.timezone('America/Los_Angeles'))
#                         if feedback_survey_release_date <= datetime.now().astimezone(
#                                 pytz.timezone('America/Los_Angeles')):
#                             assign['feedback_survey'] = 1
#                         else:
#                             assign['feedback_survey'] = 0
#                     assignments_info.append(assign)
#                 return Response({"user_role":userRole, "assignments": assignments_info}, status=status.HTTP_200_OK)

#             elif userRole == Registration.UserRole.Instructor or userRole == Registration.UserRole.TA:
#                 assignments = Assignment.objects.filter(course=course)
#                 assignments_info = []
#                 for a in assignments:
#                     feedback_survey = FeedbackSurvey.objects.filter(assignment=a)
#                     assign = dict()
#                     assign = model_to_dict(a)
#                     assign['feedback_survey'] = feedback_survey.count()
#                     if feedback_survey.count() == 1:
#                         feedback_survey_release_date = feedback_survey[0].date_released.astimezone(
#                             pytz.timezone('America/Los_Angeles'))
#                         if feedback_survey_release_date <= datetime.now().astimezone(
#                                 pytz.timezone('America/Los_Angeles')):
#                             assign['feedback_survey'] = 1
#                         else:
#                             assign['feedback_survey'] = 0
#                     assignments_info.append(assign)
#                 return Response({"user_role": userRole, "assignments": assignments_info}, status=status.HTTP_200_OK)
#             else:
#                 return Response(status=status.HTTP_401_UNAUTHORIZED)
            

#     def post(self, request, course_id, *args, **kwargs):
#         course = get_object_or_404(Course, pk=course_id)
#         user_id = get_user_pk(request)
#         user = get_object_or_404(CustomUser, id=user_id)
#         userRole = Registration.objects.get(users=user, courses=course).userRole
#         if userRole == Registration.UserRole.Student:
#             # Students are not allowed to create assignments
#             return Response(status=status.HTTP_403_FORBIDDEN)
#         elif userRole == Registration.UserRole.Instructor or userRole == Registration.UserRole.TA:
#             course = get_object_or_404(Course, pk=course_id)
#             serializer = AssignmentSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save(course=course)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
    
#     def put(self, request, course_id, *args, **kwargs):
#         course = get_object_or_404(Course, pk=course_id)
#         user_id = get_user_pk(request)
#         user = get_object_or_404(CustomUser, id=user_id)
#         userRole = Registration.objects.get(users=user, courses=course).userRole
#         if 'assignment_id' in request.query_params:
#             assignment_id = request.query_params['assignment_id']
#             if userRole == Registration.UserRole.Student:
#                 return Response(status=status.HTTP_403_FORBIDDEN)
#             elif userRole == Registration.UserRole.Instructor or userRole == Registration.UserRole.TA:
#                 assignment = get_object_or_404(Assignment, pk=assignment_id)
#                 serializer = AssignmentSerializer(assignment, data=request.data)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data)
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 # user role not found
#                 return Response(status=status.HTTP_401_UNAUTHORIZED)
#         else:
#             # missing data, return 400
#             return Response(status=status.HTTP_400_BAD_REQUEST)
        
#     def delete(self, request, course_id, *args, **kwargs):
#         course = get_object_or_404(Course, pk=course_id)
#         user_id = get_user_pk(request)
#         user = get_object_or_404(CustomUser, id=user_id)
#         userRole = Registration.objects.get(users=user, courses=course).userRole
#         if 'assignment_id' in request.query_params:
#             assignment_id = request.query_params['assignment_id']
#             if userRole == Registration.UserRole.Student:
#                 return Response(status=status.HTTP_403_FORBIDDEN)
#             elif userRole == Registration.UserRole.Instructor or userRole == Registration.UserRole.TA:
#                 assignment = get_object_or_404(Assignment, pk=assignment_id)
#                 assignment.delete()
#                 # return 200 or 204
#                 return Response(status=status.HTTP_204_NO_CONTENT)
#             else:
#                 # user role not found
#                 return Response(status=status.HTTP_401_UNAUTHORIZED)
#         else:
#             # missing data, return 400
#             return Response(status=status.HTTP_400_BAD_REQUEST)
            
