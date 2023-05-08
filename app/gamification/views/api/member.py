from django.http import HttpResponse
from app.gamification import serializers
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from django.contrib import messages
from app.gamification.serializers import EntitySerializer
from django.shortcuts import get_object_or_404
from app.gamification.models import Assignment, Course, CustomUser, Registration, UserRole, Team, Membership, Artifact, ArtifactReview, Entity
import pytz
from pytz import timezone
from datetime import datetime

from app.gamification.utils.auth import get_user_pk

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
class MemberList(generics.RetrieveUpdateDestroyAPIView):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
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
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'andrew_id': openapi.Schema(type=openapi.TYPE_STRING),
                            'userRole': openapi.Schema(type=openapi.TYPE_STRING),
                            'team': openapi.Schema(type=openapi.TYPE_STRING),
                            'is_activated': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        }
                    )
                )
            )
        }
    )
    def get(self, request, course_id, *args, **kwargs):
        try: 
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({ 'message': 'Could not find course.'},  status=status.HTTP_404_NOT_FOUND)
        registrations = Registration.objects.filter(course=course)
        members = []
        for registration in registrations:
            if registration.team is None:
                team = ''
            else:
                team = registration.team.name
            members.append({
                'andrew_id': registration.user.andrew_id,
                'userRole': registration.userRole,
                'team': team,
                'is_activated': registration.user.is_activated
            })
        return Response(members, status=status.HTTP_200_OK)
    '''
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
            role = request.data.get('userRole')
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
            team_name = request.data.get('team')
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
        print('registration', registration)
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
            print(registration)
            delete_memebership_after_switch_to_TA_or_instructor(
                registration)
            get_users_team(registration, request)
        except CustomUser.DoesNotExist:
            return Response({'error': 'AndrewID does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        messages.info(request, error_info)

        context = get_member_list(course_id)
        context["user_role"] = userRole
        return Response(context)

    '''

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
            201: openapi.Response(
                description='New member details',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'andrew_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'userRole': openapi.Schema(type=openapi.TYPE_STRING),
                        'team': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_activated': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    }
                )
            )
        }
    )
    def post(self, request, course_id, *args, **kwargs):
        def create_member(user, users, andrew_id, userRole):
            if user not in users:
                registration = Registration(
                    user=user, course=course, userRole=userRole
                )
                registration.save()
            else:
                registration = get_object_or_404(
                    Registration, user=user, course=course)
                registration.userRole = userRole
                registration.save()
            return registration

        # Create membership for new team
        def create_team_membership(new_team, registration):
            team = registration.team
            if team is not None:
                membership = get_object_or_404(Membership, stuent=registration, entity=team)
                membership.delete()
                if len(team.members) == 0:
                    team.delete()
                else:
                    # Add all artifact reviews for registration
                    artifacts = Artifact.objects.filter(entity=team)
                    for artifact in artifacts:
                        artifact_review = ArtifactReview(
                            artifact=artifact, user=registration)
                        artifact_review.save()
            try:
                team = Team.objects.get(
                    course=course, name=new_team)
            except Team.DoesNotExist:
                team = Team(course=course, name=new_team)
                team.save()
            membership = Membership(student=registration, entity=team)
            membership.save()

            # Delete artifact reviews for updated team
            artifacts = Artifact.objects.filter(entity=team)
            for artifact in artifacts:
                ArtifactReview.objects.filter(
                    artifact=artifact, user=registration).delete()

        # Delete student data if switching to TA/Instructor
        def delete_membership(registration):
            # Delete team consisting of only 1 individual
            membership = Membership.objects.filter(student=registration)
            if membership.exists():
                team = Team.objects.filter(
                    registration=registration, course=course)
                if team.exists():
                    team = team[0]
                if len(team.members) == 1:
                    team.delete()
            membership.delete()
            # Delete all artifact_reviews of TA or instructor
            artifact_reviews = ArtifactReview.objects.filter(
                user=registration)
            for artifact_review in artifact_reviews:
                artifact_review.delete()

        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, pk=user_id)
        registration = get_object_or_404(
            Registration, user=user, course=course)
        creator_role = registration.userRole

        if creator_role != UserRole.Instructor:
            return Response({ 'message': 'Only instructors can add users.' }, status=status.HTTP_400_BAD_REQUEST)
        
        andrew_id = request.data.get('andrew_id')
        userRole = request.data.get('userRole')
        team = request.data.get('team')
        if andrew_id is None:
            return Response({'error': 'AndrewID is missing'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if userRole == UserRole.Instructor and self.check_instructor_count(course_id) <= 1:
                return Response({'error': 'You are the last instructor, you cannot switch to student or TA'}, status=status.HTTP_400_BAD_REQUEST)
            new_user = CustomUser.objects.get(andrew_id=andrew_id)
            current_members = []
            current_members.extend(course.students)
            current_members.extend(course.TAs)
            current_members.extend(course.instructors)
            registration = create_member(new_user, current_members, andrew_id=andrew_id, userRole=userRole)

            if registration.userRole == UserRole.TA or registration.userRole == UserRole.Instructor:
                delete_membership(registration)

            if registration.userRole == UserRole.Student and team != '':
                create_team_membership(team, registration)
        except CustomUser.DoesNotExist:
            return Response({'error': 'AndrewID does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        response_data = {
            'andrew_id': new_user.andrew_id,
            'team': team,
            'is_activated': new_user.is_activated,
            'userRole': registration.userRole
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_description="Delete a user from a course",
        tags=['members'],
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
            return Response({'message': 'AndrewID is missing'}, status=status.HTTP_400_BAD_REQUEST)
        andrew_id = request.query_params['andrew_id']
        user_to_delete = get_object_or_404(CustomUser, andrew_id=andrew_id)
        registration = get_object_or_404(
            Registration, user=user_to_delete, course=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, pk=user_id)
        deletorRegistration = get_object_or_404(Registration, user=user)
        if deletorRegistration.userRole != UserRole.Instructor:
            return Response({'message': 'Only instructor can delete members.'}, status=status.HTTP_401_UNAUTHORIZED)

        if registration.userRole == UserRole.Instructor and self.check_instructor_count(course_id) <= 1:
            return Response({'message': 'Cannot delete the last instructor'}, status=status.HTTP_400_BAD_REQUEST)

        # Delete all the user's artifact reviews
        ArtifactReview.objects.filter(user=registration).delete()

        # Delete all the user's artifacts
        entity = Entity.objects.filter(registration=registration)
        if entity.exists() and entity.number_members == 1:
            Artifact.objects.filter(entity=entity).delete()
            entity.delete()
        
        membership = Membership.objects.filter(student=registration)
        membership.delete()
        registration.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
