from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from app.gamification.serializers import CourseSerializer, AssignmentSerializer
from django.shortcuts import get_object_or_404, redirect, render
from app.gamification.models import Assignment, Course, Registration, Team, Membership, Artifact, Individual, FeedbackSurvey
import pytz
from pytz import timezone

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
    
class AssignmentListForAdmin(generics.ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        userRole = Registration.objects.get(users=request.user, courses=course).userRole
        assignments = Assignment.objects.filter(course=course)
        info = []
        for a in assignments:
            feedback_survey = FeedbackSurvey.objects.filter(assignment=a)
            assign = dict()
            assign['assignment'] = a
            assign['feedback_survey'] = feedback_survey.count()
            if feedback_survey.count() == 1:
                feedback_survey_release_date = feedback_survey[0].date_released.astimezone(
                    pytz.timezone('America/Los_Angeles'))
                if feedback_survey_release_date <= datetime.now().astimezone(
                        pytz.timezone('America/Los_Angeles')):
                    assign['feedback_survey'] = 1
                else:
                    assign['feedback_survey'] = 0
            info.append(assign)
        context = {'infos': info,
                   "course_id": course_id,
                   "course": course,
                   "userRole": userRole}
        return render(request, 'assignment.html', context)
        

class AssignmentListForStudent(generics.ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        userRole = Registration.objects.get(
        users=request.user, courses=course).userRole
        infos = Assignment.objects.filter(course=course)
        user_is_individual = True
        try:
            registration = get_object_or_404(
                Registration, users=request.user, courses=course_id)
            entity = Team.objects.get(
                registration=registration, course=course)
            user_is_individual = False
        except Team.DoesNotExist:
            user_is_individual = True
        assignments = []
        for assignment in infos:
            assignment_type = assignment.assignment_type
            if assignment_type == 'Team' and user_is_individual:
                print('individual user can not see this assignment')
            else:
                if assignment.date_released != None and assignment.date_released.astimezone(pytz.timezone('America/Los_Angeles')) <= datetime.now().astimezone(
                        pytz.timezone('America/Los_Angeles')):
                    assignments.append(assignment)
                elif assignment.date_released == None:
                    assignments.append(assignment)
        info = []
        for a in assignments:
            feedback_survey = FeedbackSurvey.objects.filter(assignment=a)
            assign = dict()
            assign['assignment'] = a
            assign['feedback_survey'] = feedback_survey.count()
            if feedback_survey.count() == 1:
                feedback_survey_release_date = feedback_survey[0].date_released.astimezone(
                    pytz.timezone('America/Los_Angeles'))
                if feedback_survey_release_date <= datetime.now().astimezone(
                        pytz.timezone('America/Los_Angeles')):
                    assign['feedback_survey'] = 1
                else:
                    assign['feedback_survey'] = 0
            info.append(assign)
        context = {'infos': info,
                   "course_id": course_id,
                   "course": course,
                   "userRole": userRole}
        # return render(request, 'assignment.html', context)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)