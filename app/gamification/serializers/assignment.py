from rest_framework import serializers

from app.gamification.models import Assignment


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['pk', 'course', 'assignment_name','description', 'assignment_type', 
                  'submission_type', 'total_score', 'weight', 'date_created', 
                  'date_released', 'date_due', 'review_assign_policy', 'ipsatization_min', 'ipsatization_max']
