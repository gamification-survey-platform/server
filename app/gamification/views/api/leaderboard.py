from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response

from app.gamification.models import Course, CustomUser, Registration
from app.gamification.serializers import UserSerializer
from app.gamification.utils.s3 import generate_presigned_url


class PlatformLeaderboard(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        users = CustomUser.objects.filter(is_staff=False)
        response_data = []
        for user in users:
            image = None
            if settings.USE_S3 and user.image:
                download_url = generate_presigned_url(str(user.image), http_method="GET")
                image = download_url
            elif user.image:
                download_url = f"http://{settings.ALLOWED_HOSTS[2]}:8000{user.image.url}"
                image = download_url
            response_data.append(
                {"andrew_id": user.andrew_id, "date_joined": user.date_joined, "image": image, "exp": user.exp}
            )
        return Response(response_data)


class CourseLeaderboard(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id)
        registrations = Registration.objects.filter(course=course)
        response_data = []
        for registration in registrations:
            image = None
            user = registration.user
            if user.is_staff:
                continue
            if settings.USE_S3 and user.image:
                download_url = generate_presigned_url(str(user.image), http_method="GET")
                image = download_url
            elif user.image:
                download_url = f"http://{settings.ALLOWED_HOSTS[2]}:8000{user.image.url}"
                image = download_url
            response_data.append(
                {
                    "andrew_id": user.andrew_id,
                    "date_joined": user.date_joined,
                    "image": image,
                    "course_experience": registration.course_experience,
                }
            )
        return Response(response_data)
