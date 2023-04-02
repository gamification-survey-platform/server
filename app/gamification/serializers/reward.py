from rest_framework import serializers
from app.gamification.models import Reward


class RewardSerializer(serializers.ModelSerializer):
    picture = serializers.FileField()

    class Meta:
        model = Reward
        fields = ('pk', 'name', 'description', 'course', 'type',
                  'inventory', 'is_active', 'picture', 'quantity', 'theme', 'exp_point')

    def to_representation(self, instance):
        return self.type_serializer(instance)

    def type_serializer(self, reward):
        data = {}
        data['pk'] = reward.pk
        data['name'] = reward.name
        data['description'] = reward.description
        data['belong_to'] = reward.course.course_name
        data['type'] = reward.reward_type.type
        data['is_active'] = reward.is_active
        data['exp_points'] = reward.exp_point
        if reward.inventory == -1:
            data['inventory'] = 'Unlimited'
        else:
            data['inventory'] = reward.inventory
        if reward.reward_type.type == 'Badge':
            data['picture'] = reward.picture.url
        elif reward.reward_type.type == 'Bonus' or reward.reward_type.type == 'Late Submission':
            data['quantity'] = reward.quantity
        elif reward.reward_type.type == 'Theme':
            data['theme'] = reward.theme
        elif reward.reward_type.type == 'Other':
            data['picture'] = reward.picture.url
        return data
