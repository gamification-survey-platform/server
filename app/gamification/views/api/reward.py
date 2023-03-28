from app.gamification.models.course import Course
from app.gamification.models.reward import Reward
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from app.gamification.models.user import CustomUser
from app.gamification.utils import get_user_pk
from app.gamification.serializers.reward import RewardSerializer
from django.shortcuts import get_object_or_404


class RewardList(generics.ListCreateAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    def get(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        rewards = Reward.objects.all()
        serializer = self.get_serializer(rewards, many=True)
        return Response(serializer.data)


class RewardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    def get(self, request, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        serializer = self.get_serializer(reward)
        return Response(serializer.data)

    def patch(self, request, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        is_active = request.data.get('is_active')
        if not user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        reward.is_active = True if is_active == 'true' else False
        reward.save()
        serializer = self.get_serializer(reward)
        return Response(serializer.data)

    def delete(self, request, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        reward.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class courseRewardList(generics.ListCreateAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    def get(self, request, course_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        rewards = Reward.objects.filter(course_id=course_id)
        serializer = self.get_serializer(rewards, many=True)
        return Response(serializer.data)

    def post(self, request, course_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        course = get_object_or_404(Course, pk=course_id)
        name = request.data.get('name')
        description = request.data.get('description')
        type = request.data.get('type')
        inventory = request.data.get('inventory')
        is_active = request.data.get('is_active')
        exp_point = request.data.get('exp_points')
        reward = Reward.objects.create()
        if exp_point:
            reward.exp_point = exp_point
        if inventory:
            reward.inventory = inventory
        if type:
            reward.type = type
        if is_active:
            reward.is_active = True if is_active == 'true' else False
        reward.course = course
        reward.name = name
        reward.description = description
        if type == 'Bonus' or type == 'Late Submission':
            reward.quantity = request.data.get('quantity')
        elif type == 'Badge' or type == 'Other':
            reward.picture = request.data.get('picture')
        else:
            return Response(message="Invalid reward type", status=status.HTTP_400_BAD_REQUEST)
        reward.save()
        serializer = self.get_serializer(reward)
        return Response(serializer.data)


class courseRewardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reward.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer

    def get(self, request, course_id, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        serializer = self.get_serializer(reward)
        return Response(serializer.data)

    def patch(self, request, course_id, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        name = request.data.get('name')
        description = request.data.get('description')
        type = request.data.get('type')
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
            reward.type = type
        if inventory:
            reward.inventory = inventory
        if is_active:
            reward.is_active = True if is_active == 'true' else False
        if type == 'Bonus' or type == 'Late Submission':
            quantity = request.data.get('quantity')
            if quantity:
                reward.quantity = quantity
        elif type == 'Badge' or type == 'Other':
            picture = request.data.get('picture')
            if picture:
                reward.picture = picture
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        reward.save()
        serializer = self.get_serializer(reward)
        return Response(serializer.data)

    def delete(self, request, course_id, reward_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        reward = Reward.objects.get(pk=reward_id)
        reward.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
