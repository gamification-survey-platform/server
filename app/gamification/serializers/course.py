from rest_framework import serializers

from app.gamification.models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["pk", "course_number", "course_name", "syllabus", "semester", "visible", "picture"]
