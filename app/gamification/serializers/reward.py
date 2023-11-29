from django.conf import settings
from rest_framework import serializers

from app.gamification.models import Reward, UserReward
from app.gamification.utils.s3 import generate_presigned_url


class RewardSerializer(serializers.ModelSerializer):
    picture = serializers.FileField()
    picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Reward
        fields = (
            "pk",
            "name",
            "description",
            "course",
            "reward_type",
            "inventory",
            "is_active",
            "picture",
            "quantity",
            "points",
            "picture_url",
        )

    def get_picture_url(self, obj):
        if settings.USE_S3 and obj.picture:
            key = obj.picture.name
            return generate_presigned_url(key, http_method="GET")
        return None

    def to_representation(self, instance):
        data = self.type_serializer(instance)

        return data

    def type_serializer(self, reward):
        owners = UserReward.objects.filter(reward=reward)
        data = {}
        data["pk"] = reward.pk
        data["name"] = reward.name
        data["description"] = reward.description
        data["belong_to"] = reward.course.course_name
        data["type"] = reward.reward_type
        data["is_active"] = reward.is_active
        data["points"] = reward.points
        data["owners"] = [i.user.andrew_id for i in owners]
        if reward.picture:
            if hasattr(reward.picture, 'url'):
                path = f"http://{settings.ALLOWED_HOSTS[2]}:8000{reward.picture.url}"
                data["picture"] = self.get_picture_url(reward) if settings.USE_S3 else path
            else:
                data["picture"] = None
        else:
            data["picture"] = None
        if reward.inventory == -1:
            data["inventory"] = "Unlimited"
        else:
            data["inventory"] = reward.inventory
        if reward.reward_type == Reward.RewardType.BONUS or reward.reward_type == Reward.RewardType.LATE_SUBMISSION:
            data["quantity"] = reward.quantity
        return data