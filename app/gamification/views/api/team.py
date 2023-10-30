from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models import (
    Artifact,
    ArtifactReview,
    Course,
    CustomUser,
    Entity,
    Individual,
    Membership,
    Registration,
    Team,
)
from app.gamification.serializers import EntitySerializer
from app.gamification.utils.auth import get_user_pk


class TeamList(generics.RetrieveUpdateDestroyAPIView):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get a list of teams in a course",
        tags=["teams"],
        responses={
            200: openapi.Response(
                description="List of teams",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "andrew_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "is_staff": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "team": openapi.Schema(type=openapi.TYPE_STRING),
                            "is_activated": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        },
                    ),
                ),
            )
        },
    )
    def get(self, request, course_id, *args, **kwargs):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"message": "Could not find course."}, status=status.HTTP_404_NOT_FOUND)
        teams = Team.objects.filter(course=course)
        res_teams = []
        for team in teams:
            if team.team is None:
                team = ""
            else:
                team = team.name
            res_teams.append(
                {
                    "team_id": team,
                }
            )
        print("teams: ", res_teams)
        return Response(res_teams, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Add a member to a course",
        tags=["members"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "andrew_id": openapi.Schema(type=openapi.TYPE_STRING),
                "team": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            201: openapi.Response(
                description="New member details",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "andrew_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "is_staff": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "team": openapi.Schema(type=openapi.TYPE_STRING),
                        "is_activated": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
            )
        },
    )
    def post(self, request, course_id, *args, **kwargs):
        def create_member(user, users, andrew_id):
            if user not in users:
                registration = Registration(user=user, course=course)
                registration.save()
                individual = Individual(course=course)
                individual.save()
                membership = Membership(student=registration, entity=individual)
                membership.save()
            else:
                registration = get_object_or_404(Registration, user=user, course=course)
                registration.save()
            return registration

        # Create membership for new team
        def create_team_membership(new_team, registration):
            team = registration.team
            if team is not None:
                membership = get_object_or_404(Membership, student=registration, entity=team)
                membership.delete()
                if len(team.members) == 0:
                    team.delete()
                else:
                    # Add all artifact reviews for registration
                    artifacts = Artifact.objects.filter(entity=team)
                    for artifact in artifacts:
                        artifact_review = ArtifactReview(artifact=artifact, user=registration)
                        artifact_review.save()
            try:
                team = Team.objects.get(course=course, name=new_team)
            except Team.DoesNotExist:
                team = Team(course=course, name=new_team)
                team.save()
            membership = Membership(student=registration, entity=team)
            membership.save()

            # Delete artifact reviews for updated team
            artifacts = Artifact.objects.filter(entity=team)
            for artifact in artifacts:
                ArtifactReview.objects.filter(artifact=artifact, user=registration).delete()

        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, pk=user_id)
        registration = get_object_or_404(Registration, user=user, course=course)

        if not user.is_staff:
            return Response({"message": "Only instructors can add users."}, status=status.HTTP_400_BAD_REQUEST)

        andrew_id = request.data.get("andrew_id")
        team = request.data.get("team")
        if andrew_id is None:
            return Response({"message": "AndrewID is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if user.andrew_id == andrew_id:
                return Response(
                    {"message": "Cannot modify your own role."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            new_user = CustomUser.objects.get(andrew_id=andrew_id)
            current_members = []
            course_registrations = Registration.objects.filter(course=course)
            for registration in course_registrations:
                current_members.append(registration.user)
            registration = create_member(new_user, current_members, andrew_id=andrew_id)

            if not new_user.is_staff and team != "":
                create_team_membership(team, registration)
        except CustomUser.DoesNotExist:
            return Response({"message": "AndrewID does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "andrew_id": new_user.andrew_id,
            "team": team,
            "is_activated": new_user.is_activated,
            "is_staff": new_user.is_staff,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Delete a user from a course",
        tags=["members"],
        manual_parameters=[
            openapi.Parameter(
                "andrew_id",
                openapi.IN_QUERY,
                description="Andrew ID of the user to be deleted",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response("Success"),
            400: openapi.Response("Bad Request"),
            404: openapi.Response("Not Found"),
        },
    )
    def delete(self, request, course_id, *args, **kwargs):
        if "andrew_id" not in request.query_params:
            return Response({"message": "AndrewID is missing"}, status=status.HTTP_400_BAD_REQUEST)
        andrew_id = request.query_params["andrew_id"]
        user_to_delete = get_object_or_404(CustomUser, andrew_id=andrew_id)
        registration = get_object_or_404(Registration, user=user_to_delete, course=course_id)
        user_id = get_user_pk(request)
        course = get_object_or_404(Course, id=course_id)
        user = get_object_or_404(CustomUser, pk=user_id)
        if not user.is_staff:
            return Response({"message": "Only instructor can delete members."}, status=status.HTTP_401_UNAUTHORIZED)

        instructor_count = 0
        course_registrations = Registration.objects.filter(course=course)
        for registration in course_registrations:
            if registration.user.is_staff:
                instructor_count += 1
        if user_to_delete.is_staff and instructor_count <= 1:
            return Response({"message": "Cannot delete the last instructor"}, status=status.HTTP_400_BAD_REQUEST)

        # Delete all the user's artifact reviews
        ArtifactReview.objects.filter(user=registration).delete()

        # Delete all the user's artifacts
        entity = Entity.objects.filter(registration=registration)
        if entity.exists() and entity[0].number_members == 1:
            Artifact.objects.filter(entity=entity[0]).delete()
            entity[0].delete()

        membership = Membership.objects.filter(student=registration)
        membership.delete()
        registration.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


    @swagger_auto_schema(
        operation_description="Update a member's team in a course",
        tags=["members"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "andrew_id": openapi.Schema(type=openapi.TYPE_STRING),
                "team": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(
                description="Updated member details",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "andrew_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "is_staff": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "team": openapi.Schema(type=openapi.TYPE_STRING),
                        "is_activated": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
            )
        },
    )

    def patch(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, pk=user_id)
        def create_team_membership(new_team, registration):
            team = registration.team
            if team is not None:
                membership = get_object_or_404(Membership, student=registration, entity=team)
                membership.delete()
                if len(team.members) == 0:
                    team.delete()
                else:
                    # Add all artifact reviews for registration
                    artifacts = Artifact.objects.filter(entity=team)
                    for artifact in artifacts:
                        artifact_review = ArtifactReview(artifact=artifact, user=registration)
                        artifact_review.save()
            try:
                team = Team.objects.get(course=course, name=new_team)
            except Team.DoesNotExist:
                team = Team(course=course, name=new_team)
                team.save()
            membership = Membership(student=registration, entity=team)
            membership.save()

            # Delete artifact reviews for updated team
            artifacts = Artifact.objects.filter(entity=team)
            for artifact in artifacts:
                ArtifactReview.objects.filter(artifact=artifact, user=registration).delete()

        # Ensure the user is an instructor
        if not user.is_staff:
            return Response({"message": "Only instructors can modify users."}, status=status.HTTP_400_BAD_REQUEST)

        andrew_id = request.data.get("andrew_id")
        new_team_name = request.data.get("team_id")
        print(andrew_id, " new_team_name: ", new_team_name)

        if not andrew_id:
            return Response({"message": "AndrewID is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_user = CustomUser.objects.get(andrew_id=andrew_id)
            
            # Don't allow users to modify their own team
            if user.andrew_id == andrew_id:
                return Response({"message": "Cannot modify your own role."}, status=status.HTTP_400_BAD_REQUEST)
            
            registration = get_object_or_404(Registration, user=target_user, course=course)
            
            # If there's a team specified in the request, update the team
            if new_team_name:
                create_team_membership(new_team_name, registration)
            
        except CustomUser.DoesNotExist:
            return Response({"message": "AndrewID does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "andrew_id": target_user.andrew_id,
            "team": new_team_name,
            "is_activated": target_user.is_activated,
            "is_staff": target_user.is_staff,
        }
        return Response(response_data, status=status.HTTP_200_OK)
