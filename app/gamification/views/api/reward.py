from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.gamification.models.course import Course
from app.gamification.models.registration import Registration
from app.gamification.models.reward import Reward
from app.gamification.models.user import CustomUser
from app.gamification.models.user_reward import UserReward
from app.gamification.serializers.reward import RewardSerializer
from app.gamification.utils.auth import get_user_pk
from app.gamification.utils.s3 import generate_presigned_post, generate_presigned_url

base_reward_schema = {
    "name": openapi.Schema(type=openapi.TYPE_STRING),
    "description": openapi.Schema(type=openapi.TYPE_STRING),
    "belong_to": openapi.Schema(type=openapi.TYPE_STRING),
    "type": openapi.Schema(type=openapi.TYPE_STRING, enum=["Late Submission", "Bonus", "Other"]),
    "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
    "points": openapi.Schema(type=openapi.TYPE_INTEGER),
    "owners": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(openapi.TYPE_STRING)),
    "inventory": openapi.Schema(type=openapi.TYPE_INTEGER),
}


class RewardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    @swagger_auto_schema(
        operation_description="Update a reward",
        tags=["rewards"],
    )
    def get(self, request, reward_id, *args, **kwargs):
        reward = Reward.objects.get(pk=reward_id)
        serializer = self.get_serializer(reward)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a reward",
        tags=["rewards"],
    )
    def patch(self, request, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        is_active = request.data.get("is_active")
        if user.is_superuser:
            reward = Reward.objects.get(pk=reward_id)
            reward.is_active = True if is_active == "true" else False
            reward.save()
            serializer = self.get_serializer(reward)
            return Response(serializer.data)
        elif user.is_staff:
            pass
        else:
            reward = Reward.objects.get(pk=reward_id)
            course = reward.course
            registration = get_object_or_404(Registration, user=user, course=course)
            if reward.points > registration.points:
                return Response(data={"message": "Do not have enough points"}, status=status.HTTP_400_BAD_REQUEST)
            if reward.inventory > 0 or reward.inventory == -1:
                if reward.inventory != -1:
                    reward.inventory -= 1
                    reward.save()
                registration.points -= reward.points
                registration.save()
                user_reward = UserReward.objects.create(user=user, reward=reward)
                user_reward.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(data={"message": "Reward is out of stock"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a reward",
        tags=["rewards"],
    )
    def delete(self, request, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        reward.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def generate_reward_key(request, course):
    picture = request.FILES.get("picture")
    if not picture:
        return None

    content_type = picture.content_type
    if content_type == "image/jpeg":
        file_ext = "jpg"
    elif content_type == "image/png":
        file_ext = "png"
    else:
        return None

    if settings.USE_S3:
        key = f"rewards/reward_{course.id}.{file_ext}"
    else:
        key = picture

    return key


class CourseRewardList(generics.ListCreateAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    @swagger_auto_schema(
        operation_description="Get rewards under a course",
        tags=["rewards"],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "picture": openapi.Schema(type=openapi.TYPE_STRING),
                        **base_reward_schema,
                    },
                ),
            )
        },
    )
    def get(self, request, course_id, *args, **kwargs):
        # Course ID = -1 indicates System Level rewards
        if course_id == -1:
            sys_pk = settings.SYSTEM_PK
            rewards = []
            rewards.extend(Reward.objects.filter(course=sys_pk, is_active=True))
            serializer = self.get_serializer(rewards, many=True)
            return Response(serializer.data)
        else:
            rewards = Reward.objects.filter(course_id=course_id)
            serializer = self.get_serializer(rewards, many=True)
            return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a reward under a course",
        tags=["rewards"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"picture": openapi.Schema(type=openapi.TYPE_FILE), **base_reward_schema},
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "upload_url": openapi.Schema(type=openapi.TYPE_STRING),
                    "download_url": openapi.Schema(type=openapi.TYPE_STRING),
                    **base_reward_schema,
                },
            )
        },
    )
    def post(self, request, course_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response({"message": "Only instructors can create rewards"}, status=status.HTTP_403_FORBIDDEN)
        course = get_object_or_404(Course, pk=course_id)
        name = request.data.get("name")
        description = request.data.get("description")
        type = request.data.get("type")
        inventory = int(request.data.get("inventory"))
        is_active = request.data.get("is_active")
        points = int(request.data.get("points"))
        reward = Reward.objects.create(
            course=course,
            reward_type=type,
        )
        if points:
            reward.points = points
        if inventory:
            reward.inventory = inventory
        if is_active:
            reward.is_active = True if is_active == "true" else False
        if name:
            reward.name = name
        if description:
            reward.description = description
        if type == Reward.RewardType.BONUS or type == Reward.RewardType.LATE_SUBMISSION:
            reward.quantity = request.data.get("quantity")
        elif type == Reward.RewardType.OTHER:
            picture_key = generate_reward_key(request, course)
            reward.picture = picture_key
        else:
            return Response({"message": "Invalid reward type."}, status=status.HTTP_400_BAD_REQUEST)
        reward.save()
        response_data = self.get_serializer(reward).data
        if type == Reward.RewardType.OTHER:
            if settings.USE_S3:
                upload_url = generate_presigned_post(picture_key)
                download_url = generate_presigned_url(picture_key, http_method="GET")
            else:
                upload_url = response_data["picture"]
                download_url = response_data["picture"]

            response_data.pop("picture")
            if upload_url:
                response_data["upload_url"] = upload_url
            if download_url:
                response_data["download_url"] = download_url
        return Response(response_data)


class CourseRewardPurchases(generics.RetrieveUpdateAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    @swagger_auto_schema(
        operation_description="Get all course reward purchases",
        tags=["Rewards"],
        responses={
            200: openapi.Response(
                description="All rewards purchased within a course",
            )
        },
    )
    def get(self, request, course_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        response_data = []
        course_rewards = Reward.objects.filter(course_id=course_id)
        for course_reward in course_rewards:
            purchased_course_rewards = UserReward.objects.filter(reward_id=course_reward.id)
            for purchased_course_reward in purchased_course_rewards:
                buyer = CustomUser.objects.get(id=purchased_course_reward.user_id)
                reward_data = self.get_serializer(course_reward).data
                reward_data["reward_id"] = reward_data["pk"]
                reward_data["pk"] = purchased_course_reward.pk
                reward_data["buyer"] = buyer.andrew_id
                reward_data["fulfilled"] = purchased_course_reward.fulfilled
                reward_data["date_purchased"] = purchased_course_reward.date_purchased
                response_data.append(reward_data)

        return Response(response_data, status=status.HTTP_200_OK)


class CourseRewardPurchasesDetail(generics.UpdateAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    @swagger_auto_schema(
        operation_description="Edit a course purchase",
        tags=["Rewards"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
        ),
        responses={204: openapi.Response(description="No content.")},
    )
    def patch(self, request, course_id, purchase_id, *args, **kwargs):
        purchase = get_object_or_404(UserReward, id=purchase_id)
        fulfilled = request.data.get("fulfilled")
        if fulfilled is not None:
            purchase.fulfilled = fulfilled
            purchase.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRewardPurchases(generics.RetrieveUpdateAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    @swagger_auto_schema(
        operation_description="Get all user's purchases",
        tags=["Rewards"],
        responses={
            200: openapi.Response(
                description="All rewards purchased by a user",
            )
        },
    )
    def get(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        response_data = []
        user_rewards = UserReward.objects.filter(user_id=user_id)
        for user_reward in user_rewards:
            reward = Reward.objects.get(id=user_reward.reward_id)
            reward_data = self.get_serializer(reward).data
            reward_data["fulfilled"] = user_reward.fulfilled
            reward_data["date_purchased"] = user_reward.date_purchased
            response_data.append(reward_data)

        return Response(response_data, status=status.HTTP_200_OK)


class CourseRewardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    @swagger_auto_schema(
        operation_description="Get a reward under a course",
        tags=["rewards"],
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
        tags=["rewards"],
    )
    def patch(self, request, course_id, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response({"message": "Only instructors can update rewards"}, status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        course = get_object_or_404(Course, pk=course_id)
        name = request.data.get("name")
        description = request.data.get("description")
        reward_type = request.data.get("type")
        inventory = request.data.get("inventory")
        is_active = request.data.get("is_active")
        points = request.data.get("points")
        if name:
            reward.name = name
        if description:
            reward.description = description
        if points:
            reward.points = points
        if reward_type:
            reward.reward_type = reward_type
        if inventory:
            reward.inventory = inventory
        if is_active:
            reward.is_active = True if is_active == "true" else False
        if reward_type == Reward.RewardType.BONUS or reward_type == Reward.RewardType.LATE_SUBMISSION:
            quantity = request.data.get("quantity")
            if quantity:
                reward.quantity = quantity
        elif reward_type == Reward.RewardType.OTHER:
            picture_key = generate_reward_key(request, course)
            reward.picture = picture_key
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        reward.save()
        serializer = self.get_serializer(reward)
        response_data = serializer.data
        if reward_type == Reward.RewardType.OTHER:
            if settings.USE_S3:
                upload_url = generate_presigned_post(picture_key)
                download_url = generate_presigned_url(picture_key, http_method="GET")
                delete_url = generate_presigned_url(str(reward.picture), http_method="DELETE")
            else:
                upload_url = response_data["picture"]
                download_url = response_data["picture"]
                delete_url = None
            response_data.pop("picture")
            if upload_url:
                response_data["upload_url"] = upload_url
            if download_url:
                response_data["download_url"] = download_url
            if delete_url:
                response_data["delete_url"] = delete_url

        return Response(response_data)

    @swagger_auto_schema(
        operation_description="Delete a reward under a course",
        tags=["rewards"],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT, properties={"delete_url": openapi.Schema(type=openapi.TYPE_STRING)}
            )
        },
    )
    def delete(self, request, course_id, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        if reward.picture and settings.USE_S3:
            delete_url = generate_presigned_url(str(reward.picture), http_method="DELETE")
        reward.delete()
        response_data = {"delete_url": delete_url}
        return Response(response_data)
