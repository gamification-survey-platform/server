from rest_framework import serializers

from app.gamification.models import Theme


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = [
            "name",
            "is_published",
            "creator",
            "colorBgBase",
            "colorTextBase",
            "colorPrimary",
            "colorSuccess",
            "colorWarning",
            "colorError",
            "cursor",
            "multiple_choice_item",
            "multiple_choice_target",
            "scale_multiple_choice_item",
            "scale_multiple_choice_target",
            "multiple_select_item",
            "multiple_select_target",
        ]
