from rest_framework import serializers
from app.gamification.models import Reward
from app.gamification.models import UserReward
from django.conf import settings
from app.gamification.utils import generate_presigned_url


class RewardSerializer(serializers.ModelSerializer):
    picture = serializers.FileField()
    picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Reward
        fields = ('pk', 'name', 'description', 'course', 'reward_type',
                  'inventory', 'is_active', 'picture', 'quantity', 'theme', 'exp_point', 'picture_url')

    def get_picture_url(self, obj):
        if settings.USE_S3 and obj.picture:
            key = obj.picture.name
            return generate_presigned_url(key, http_method='GET')
        return None

    def to_representation(self, instance):
        data = self.type_serializer(instance)

        return data

    def type_serializer(self, reward):
        owner = UserReward.objects.filter(reward=reward)
        data = {}
        data['pk'] = reward.pk
        data['name'] = reward.name
        data['description'] = reward.description
        data['belong_to'] = reward.course.course_name
        data['type'] = reward.reward_type.type
        data['is_active'] = reward.is_active
        data['exp_points'] = reward.exp_point
        data['owner'] = [i.user.andrew_id for i in owner]
        data['consumed'] = len(owner)
        if reward.inventory == -1:
            data['inventory'] = 'Unlimited'
        else:
            data['inventory'] = reward.inventory
        if reward.reward_type.type == 'Bonus' or reward.reward_type.type == 'Late Submission':
            data['quantity'] = reward.quantity
        elif reward.reward_type.type == 'Other':
            path = f'http://{settings.ALLOWED_HOSTS[1]}:8000{reward.picture.url}'
            data['picture'] = self.get_picture_url(
                reward) if settings.USE_S3 else path
        return data
