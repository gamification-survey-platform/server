from django.http import HttpResponse
from app.gamification import serializers
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from django.contrib import messages
from app.gamification.serializers import EntitySerializer
from django.shortcuts import get_object_or_404
from app.gamification.models import Assignment, Course, CustomUser, Registration, Team, Membership, Artifact, ArtifactReview, Entity
import pytz
from pytz import timezone
from datetime import datetime

from app.gamification.utils import get_user_pk

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


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


class MemberList(generics.RetrieveUpdateDestroyAPIView):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    # [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def check_instructor_count(self, course_id):
        instructor_count = Registration.objects.filter(
            course=course_id, userRole='Instructor').count()
        return instructor_count

    @swagger_auto_schema(
        operation_description="Get a list of members in a course",
        tags=['members'],
        responses={
            200: openapi.Response(
                description='List of members',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'andrew_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'userRole': openapi.Schema(type=openapi.TYPE_STRING),
                        'team': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_activated': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'course_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'userRole': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def get(self, request, course_id, *args, **kwargs):
        def get_member_list(course_id):
            registration = Registration.objects.filter(course=course)
            membership = []
            for i in registration:
                try:
                    get_registration_team = Team.objects.filter(registration=i)
                    if len(get_registration_team) > 1:
                        team = get_registration_team[len(
                            get_registration_team) - 1].name
                    else:
                        team = Team.objects.get(registration=i).name
                except Team.DoesNotExist:
                    team = ''
                membership.append({
                    'andrew_id': i.user.andrew_id,
                    'userRole': i.userRole,
                    'team': team,
                    'is_activated': i.user.is_activated,
                })
            membership = sorted(membership, key=lambda x: x['team'])
            context = {'membership': membership,
                       'course_id': course_id, 'userRole': userRole}
            return context

        def get_a_member(course_id, andrew_id):
            # get user with andrew_id
            user = get_object_or_404(CustomUser, andrew_id=andrew_id)
            registration = Registration.objects.filter(
                course=course, user=user)
            membership = []
            for i in registration:
                try:
                    get_registration_team = Team.objects.filter(registration=i)
                    if len(get_registration_team) > 1:
                        team = get_registration_team[len(
                            get_registration_team) - 1].name
                    else:
                        team = Team.objects.get(registration=i).name
                except Team.DoesNotExist:
                    team = ''
                membership.append({
                    'andrew_id': i.users.andrew_id,
                    'userRole': i.userRole,
                    'team': team,
                    'is_activated': i.users.is_activated,
                })
            membership = sorted(membership, key=lambda x: x['team'])
            context = {'membership': membership,
                       'course_id': course_id, 'userRole': userRole}
            return context

        course = get_object_or_404(Course, pk=course_id)
        # TODO: rethink about permission control for staff(superuser) and instructor
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, pk=user_id)
        registration = get_object_or_404(
            Registration, user=user, course=course)
        userRole = registration.userRole
        if 'andrew_id' in request.query_params:
            andrew_id = request.query_params['andrew_id']
            context = get_a_member(course_id, andrew_id)
        else:
            context = get_member_list(course_id)
        context["user_role"] = userRole
        return Response(context)

    @swagger_auto_schema(
        operation_description="Add a member to a course",
        tags=['members'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'andrew_id': openapi.Schema(type=openapi.TYPE_STRING),
                'userRole': openapi.Schema(type=openapi.TYPE_STRING),
                'team': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description='List of members',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'andrew_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'userRole': openapi.Schema(type=openapi.TYPE_STRING),
                        'team': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_activated': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'course_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'userRole': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def post(self, request, course_id, *args, **kwargs):
        def get_member_list(course_id):
            registration = Registration.objects.filter(course=course)
            membership = []
            for i in registration:
                try:
                    get_registration_team = Team.objects.filter(registration=i)
                    if len(get_registration_team) > 1:
                        team = get_registration_team[len(
                            get_registration_team) - 1].name
                    else:
                        team = Team.objects.get(registration=i).name
                except Team.DoesNotExist:
                    team = ''
                membership.append({
                    'andrew_id': i.user.andrew_id,
                    'userRole': i.userRole,
                    'team': team,
                    'is_activated': i.user.is_activated,
                })
            membership = sorted(membership, key=lambda x: x['team'])
            context = {'membership': membership,
                       'course_id': course_id, 'userRole': userRole}
            return context

        # Create registration for user who is not registered this course, otherwise, return the registration
        def get_users_registration(users, request):
            andrew_id = request.data.get('andrew_id')
            role = request.data.get('membershipRadios')
            if user not in users:
                registration = Registration(
                    user=user, course=course, userRole=role)
                registration.save()
                error_info = 'A new member has been added'
                assignments = []
                for a in Assignment.objects.filter(course=course, assignment_type=Assignment.AssigmentType.Individual):
                    if a.date_due != None and a.date_due.astimezone(pytz.timezone('America/Los_Angeles')) < datetime.now().astimezone(pytz.timezone('America/Los_Angeles')):
                        assignments.append(a)
                    elif a.date_due == None:
                        assignments.append(a)
                for assignment in assignments:
                    artifacts = Artifact.objects.filter(assignment=assignment)
                    for artifact in artifacts:
                        artifact_review = ArtifactReview(
                            artifact=artifact, user=registration)
                        artifact_review.save()
            else:
                registration = get_object_or_404(
                    Registration, user=user, course=course)
                registration.userRole = role
                registration.save()

                error_info = andrew_id + '\'s team has been added or updated'
            return registration, error_info

        # Create membership for user's team
        def get_users_team(registration, request):
            team_name = request.data.get('team_name')
            if team_name != '' and registration.userRole == 'Student':
                team = registration.team
                if team is not None:
                    membership = get_object_or_404(
                        Membership, student=registration, entity=team)
                    membership.delete()
                    if len(team.members) == 0:
                        team.delete()
                    else:
                        # add artifact_review for previous team
                        artifacts = Artifact.objects.filter(entity=team)
                        for artifact in artifacts:
                            artifact_review = ArtifactReview(
                                artifact=artifact, user=registration)
                            artifact_review.save()

                try:
                    team = Team.objects.get(
                        course=course, name=team_name)
                except Team.DoesNotExist:
                    team = Team(course=course, name=team_name)
                    team.save()
                membership = Membership(
                    student=registration, entity=team)
                membership.save()
                # delete artifact review for updated team
                artifacts = Artifact.objects.filter(entity=team)
                for artifact in artifacts:
                    ArtifactReview.objects.filter(
                        artifact=artifact, user=registration).delete()

        # Create a list of users in the course
        def add_users_from_the_same_course():
            users = []
            users.extend(course.students)
            users.extend(course.TAs)
            users.extend(course.instructors)
            return users

        # Delete ta and instructor membership if he/she is student before
        def delete_memebership_after_switch_to_TA_or_instructor(registration):
            if registration.userRole == 'TA' or registration.userRole == 'Instructor':
                membership = Membership.objects.filter(student=registration)
                if len(membership) == 1:
                    team = Team.objects.filter(
                        registration=registration, course=course)
                    if len(team) == 1:
                        team = team[0]
                    members = team.members
                    if len(members) == 1:
                        team.delete()
                membership.delete()
                # delete all artifact_review of TA or instructor
                artifact_reviews = ArtifactReview.objects.filter(
                    user=registration)
                for artifact_review in artifact_reviews:
                    artifact_review.delete()

        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, pk=user_id)
        # TODO: rethink about permission control for staff(superuser) and instructor
        registration = get_object_or_404(
            Registration, user=user, course=course)
        userRole = registration.userRole

        andrew_id = request.data.get('andrew_id')
        if andrew_id is None:
            # missing andrew_id, return 400 bad request
            return Response({'error': 'AndrewID is missing'}, status=status.HTTP_400_BAD_REQUEST)
        # andrew_id = request.POST['andrew_id']
        try:
            # last instructor can not switch to student or TA
            if andrew_id == user.andrew_id and userRole == 'Instructor':
                instructor_count = self.check_instructor_count(course_id)
                if instructor_count <= 1:
                    return Response({'error': 'You are the last instructor, you cannot switch to student or TA'}, status=status.HTTP_400_BAD_REQUEST)

            user = CustomUser.objects.get(andrew_id=andrew_id)
            users = add_users_from_the_same_course()
            registration, error_info = get_users_registration(
                users, request)
            delete_memebership_after_switch_to_TA_or_instructor(
                registration)
            get_users_team(registration, request)
        except CustomUser.DoesNotExist:
            return Response({'error': 'AndrewID does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        messages.info(request, error_info)

        context = get_member_list(course_id)
        context["user_role"] = userRole
        return Response(context)

    @swagger_auto_schema(
        operation_description="Delete a user from a course",
        manual_parameters=[
            openapi.Parameter('andrew_id', openapi.IN_QUERY,
                              description="Andrew ID of the user to be deleted", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response('Success'),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Not Found'),
        }
    )
    def delete(self, request, course_id, *args, **kwargs):
        if 'andrew_id' not in request.query_params:
            return Response({'error': 'AndrewID is missing'}, status=status.HTTP_400_BAD_REQUEST)
        andrew_id = request.query_params['andrew_id']
        user = get_object_or_404(CustomUser, andrew_id=andrew_id)
        registration = get_object_or_404(
            Registration, user=user, course=course_id)

        if registration.userRole == 'Instructor' and self.check_instructor_count(course_id) <= 1:
            return Response({'error': 'Cannot delete the last instructor'}, status=status.HTTP_400_BAD_REQUEST)

        membership = Membership.objects.filter(student=registration)
        membership.delete()
        registration.delete()
        # delete all artifact_review of TA or instructor
        # return delete success error, return 200 or 204
        return Response(status=status.HTTP_204_NO_CONTENT)
