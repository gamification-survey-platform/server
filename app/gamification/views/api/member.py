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
    UserRole,
)
from app.gamification.serializers import EntitySerializer
from app.gamification.utils.auth import get_user_pk


class MemberList(generics.RetrieveUpdateDestroyAPIView):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [permissions.AllowAny]

    def check_instructor_count(self, course_id):
        instructor_count = Registration.objects.filter(course=course_id, userRole="Instructor").count()
        return instructor_count

    @swagger_auto_schema(
        operation_description="Get a list of members in a course",
        tags=["members"],
        responses={
            200: openapi.Response(
                description="List of members",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "andrew_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "userRole": openapi.Schema(type=openapi.TYPE_STRING),
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
        registrations = Registration.objects.filter(course=course)
        members = []
        for registration in registrations:
            if registration.team is None:
                team = ""
            else:
                team = registration.team.name
            members.append(
                {
                    "andrew_id": registration.user.andrew_id,
                    "userRole": registration.userRole,
                    "team": team,
                    "is_activated": registration.user.is_activated,
                }
            )
        return Response(members, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Add a member to a course",
        tags=["members"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "andrew_id": openapi.Schema(type=openapi.TYPE_STRING),
                "userRole": openapi.Schema(type=openapi.TYPE_STRING),
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
                        "userRole": openapi.Schema(type=openapi.TYPE_STRING),
                        "team": openapi.Schema(type=openapi.TYPE_STRING),
                        "is_activated": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
            )
        },
    )
    def post(self, request, course_id, *args, **kwargs):
        def create_member(user, users, andrew_id, userRole):
            if user not in users:
                registration = Registration(user=user, course=course, userRole=userRole)
                registration.save()
                individual = Individual(course=course)
                individual.save()
                membership = Membership(student=registration, entity=individual)
                membership.save()
            else:
                registration = get_object_or_404(Registration, user=user, course=course)
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

        # Delete student data if switching to TA/Instructor
        def delete_membership(registration):
            # Delete team consisting of only 1 individual
            membership = Membership.objects.filter(student=registration)
            if membership.exists():
                team = Team.objects.filter(registration=registration, course=course)
                if team.exists():
                    team = team[0]
                if len(team.members) == 1:
                    team.delete()
            membership.delete()
            # Delete all artifact_reviews of TA or instructor
            artifact_reviews = ArtifactReview.objects.filter(user=registration)
            for artifact_review in artifact_reviews:
                artifact_review.delete()

        course = get_object_or_404(Course, pk=course_id)
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, pk=user_id)
        registration = get_object_or_404(Registration, user=user, course=course)
        creator_role = registration.userRole

        if creator_role != UserRole.Instructor:
            return Response({"message": "Only instructors can add users."}, status=status.HTTP_400_BAD_REQUEST)

        andrew_id = request.data.get("andrew_id")
        userRole = request.data.get("userRole")
        team = request.data.get("team")
        if andrew_id is None:
            return Response({"message": "AndrewID is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if userRole == UserRole.Instructor and self.check_instructor_count(course_id) <= 1:
                return Response(
                    {"message": "You are the last instructor, you cannot switch to student or TA"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            new_user = CustomUser.objects.get(andrew_id=andrew_id)
            current_members = []
            current_members.extend(course.students)
            current_members.extend(course.TAs)
            current_members.extend(course.instructors)
            registration = create_member(new_user, current_members, andrew_id=andrew_id, userRole=userRole)

            if registration.userRole == UserRole.TA or registration.userRole == UserRole.Instructor:
                delete_membership(registration)

            if registration.userRole == UserRole.Student and team != "":
                create_team_membership(team, registration)
        except CustomUser.DoesNotExist:
            return Response({"message": "AndrewID does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "andrew_id": new_user.andrew_id,
            "team": team,
            "is_activated": new_user.is_activated,
            "userRole": registration.userRole,
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
        user = get_object_or_404(CustomUser, pk=user_id)
        deletorRegistration = get_object_or_404(Registration, user=user)
        if deletorRegistration.userRole != UserRole.Instructor:
            return Response({"message": "Only instructor can delete members."}, status=status.HTTP_401_UNAUTHORIZED)

        if registration.userRole == UserRole.Instructor and self.check_instructor_count(course_id) <= 1:
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
