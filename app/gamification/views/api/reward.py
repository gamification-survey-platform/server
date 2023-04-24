from app.gamification.models.course import Course
from app.gamification.models.registration import Registration
from app.gamification.models.reward import Reward
from app.gamification.models.xp_points import XpPoints
from app.gamification.models.reward_type import RewardType
from app.gamification.models.user_reward import UserReward
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from app.gamification.models.user import CustomUser
from app.gamification.utils import get_user_pk
from app.gamification.serializers.reward import RewardSerializer
from django.shortcuts import get_object_or_404
from django.conf import settings
from app.gamification.utils import generate_presigned_url, generate_presigned_post
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


"""
GET all rewards
Permission: Admin
"""


class RewardList(generics.ListCreateAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    @swagger_auto_schema(
        operation_description="Create a new reward",
        tags=['rewards'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'reward_type': openapi.Schema(type=openapi.TYPE_STRING),
                'course': openapi.Schema(type=openapi.TYPE_INTEGER),
                'xp_points': openapi.Schema(type=openapi.TYPE_INTEGER),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
        ),
        responses={
            200: RewardSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if user.is_superuser:
            rewards = Reward.objects.all()
            serializer = self.get_serializer(rewards, many=True)
            return Response(serializer.data)
        elif user.is_staff:
            pass
        else:
            registrations = Registration.objects.filter(users=user)
            rewards = []
            for registration in registrations:
                rewards.extend(Reward.objects.filter(
                    course=registration.courses, is_active=True))
            rewards.extend(Reward.objects.filter(
                course_id=settings.SYSTEM_PK, is_active=True))
            serializer = self.get_serializer(rewards, many=True)
            return Response(serializer.data)


"""
GET, PATCH, DELETE specific Rewards
Permissions: Admin
"""


class RewardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    @swagger_auto_schema(
        operation_description="Update a reward",
        tags=['rewards'],
    )
    def get(self, request, reward_id, *args, **kwargs):
        reward = Reward.objects.get(pk=reward_id)
        serializer = self.get_serializer(reward)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a reward",
        tags=['rewards'],
    )
    def patch(self, request, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        is_active = request.data.get('is_active')
        if user.is_superuser:
            reward = Reward.objects.get(pk=reward_id)
            reward.is_active = True if is_active == 'true' else False
            reward.save()
            serializer = self.get_serializer(reward)
            return Response(serializer.data)
        elif user.is_staff:
            pass
        else:
            reward = Reward.objects.get(pk=reward_id)
            try:
                xp_point = XpPoints.objects.get(
                    user=user)
            except XpPoints.DoesNotExist:
                xp_point = XpPoints.objects.create(
                    user=user,
                    points=0
                )
            if reward.exp_point > xp_point.points:
                return Response(data={"message": "Do not have enough points"}, status=status.HTTP_400_BAD_REQUEST)
            if reward.inventory > 0 or reward.inventory == -1:
                if reward.inventory != -1:
                    reward.inventory -= 1
                    reward.save()
                xp_point.points -= reward.exp_point
                xp_point.save()
                user_reward = UserReward.objects.create(
                    user=user,
                    reward=reward
                )
                user_reward.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(data={"message": "Reward is out of stock"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a reward",
        tags=['rewards'],
    )
    def delete(self, request, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        reward.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


"""
GET, POST Reward for a specific course
GET Permissions: Staff or Student
POST Permissions: Staff
"""


class CourseRewardList(generics.ListCreateAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    @swagger_auto_schema(
        operation_description="Get rewards under a course",
        tags=['rewards'],
    )
    def get(self, request, course_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        # Course ID = -1 indicates System Level rewards
        if course_id == -1:
            sys_pk = settings.SYSTEM_PK
            rewards = []
            rewards.extend(Reward.objects.filter(
                course=sys_pk, is_active=True))
            serializer = self.get_serializer(rewards, many=True)
            return Response(serializer.data)
        else:
            rewards = Reward.objects.filter(course_id=course_id)
            serializer = self.get_serializer(rewards, many=True)
            return Response(serializer.data)

    def create_reward_picture(self, request, course):
        picture = request.FILES.get('picture')
        if not picture:
            return None

        content_type = picture.content_type
        if content_type == 'image/jpeg':
            file_ext = 'jpg'
        elif content_type == 'image/png':
            file_ext = 'png'
        else:
            return None

        if settings.USE_S3:
            key = f'rewards/reward_{course.id}.{file_ext}'
        else:
            key = picture

        return key

    @swagger_auto_schema(
        operation_description="Create a reward under a course",
        tags=['rewards'],
    )
    def post(self, request, course_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        course = get_object_or_404(Course, pk=course_id)
        name = request.data.get('name')
        description = request.data.get('description')
        type_string = request.data.get('type')
        type = get_object_or_404(RewardType, type=type_string)
        inventory = request.data.get('inventory')
        is_active = request.data.get('is_active')
        exp_point = request.data.get('exp_points')
        reward = Reward.objects.create(
            course=course,
            reward_type=type,
        )
        if exp_point:
            reward.exp_point = exp_point
        if inventory:
            reward.inventory = inventory
        if is_active:
            reward.is_active = True if is_active == 'true' else False
        if name:
            reward.name = name
        if description:
            reward.description = description
        if type.type == 'Bonus' or type.type == 'Late Submission':
            reward.quantity = request.data.get('quantity')
        elif type.type == 'Other':
            picture_key = self.create_reward_picture(request, course)
            reward.picture = picture_key
        elif type.type == 'Theme':
            reward.theme = request.data.get('theme')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        reward.save()
        response_data = self.get_serializer(reward).data
        if type.type == 'Other' and settings.USE_S3:
            upload_url = generate_presigned_post(picture_key)
            download_url = generate_presigned_url(
                picture_key, http_method='GET')
        else:
            upload_url = response_data['picture']
            download_url = response_data['picture']

        response_data.pop('picture')
        if upload_url:
            response_data['upload_url'] = upload_url
        if download_url:
            response_data['download_url'] = download_url
        return Response(response_data)


"""
GET, PATCH, DELETE Reward for a specific course
GET Permissions: Staff or Student
PATCH, DELETE Permissions: Staff
"""


class CourseRewardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    @swagger_auto_schema(
        operation_description="Get a reward under a course",
        tags=['rewards'],
    )
    def get(self, request, course_id, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        serializer = self.get_serializer(reward)
        response_data = serializer.data

        return Response(response_data)

    @swagger_auto_schema(
        operation_description="Update a reward under a course",
        tags=['rewards'],
    )
    def patch(self, request, course_id, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if user.is_staff:
            reward = Reward.objects.get(pk=reward_id)
            name = request.data.get('name')
            description = request.data.get('description')
            type_string = request.data.get('type')
            type = get_object_or_404(RewardType, type=type_string)
            inventory = request.data.get('inventory')
            is_active = request.data.get('is_active')
            exp_point = request.data.get('exp_points')
            if name:
                reward.name = name
            if description:
                reward.description = description
            if exp_point:
                reward.exp_point = exp_point
            if type:
                reward.reward_type = type
            if inventory:
                reward.inventory = inventory
            if is_active:
                reward.is_active = True if is_active == 'true' else False
            if type.type == 'Bonus' or type.type == 'Late Submission':
                quantity = request.data.get('quantity')
                if quantity:
                    reward.quantity = quantity
            elif type.type == 'Other':
                picture = request.data.get('picture')
                if picture:
                    reward.picture = picture
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            reward.save()
            serializer = self.get_serializer(reward)
            return Response(serializer.data)
        elif user.is_superuser:
            pass
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        operation_description="Delete a reward under a course",
        tags=['rewards'],
    )
    def delete(self, request, course_id, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        reward.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
