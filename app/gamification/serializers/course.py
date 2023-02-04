from rest_framework import serializers

from app.gamification.models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_id', 'course_name',
                  'syllabus', 'semester', 'visible']
