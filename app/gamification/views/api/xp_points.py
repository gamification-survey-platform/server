from app.gamification.models.xp_points import XpPoints
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from app.gamification.models.user import CustomUser
from app.gamification.utils import get_user_pk
from app.gamification.serializers.xp_points import XpPointsSerializer
from django.shortcuts import get_object_or_404



class XpPointsList(generics.ListCreateAPIView):
    queryset = XpPoints.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = XpPointsSerializer

    def get(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        xp_points = XpPoints.objects.all()
        serializer = self.get_serializer(xp_points, many=True)
        return Response(serializer.data)
    
    # create a new xp_points
    def post(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        user = CustomUser.objects.get(pk=request.data.get('user_id'))
        points = request.data.get('points')
        exp = request.data.get('exp')
        level = request.data.get('level')
        # if user already has xp_points, update the xp_points
        if XpPoints.objects.filter(user=user).exists():
            xp_points = XpPoints.objects.get(user=user)
            xp_points.points = points
            xp_points.exp = exp
            xp_points.level = level
            xp_points.save()
            serializer = self.get_serializer(xp_points)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        xp_points = XpPoints.objects.create(
            user=user,
            points=points,
            exp=exp,
            level=level
        )
        serializer = self.get_serializer(xp_points)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class XpPointsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = XpPoints.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = XpPointsSerializer

    def get(self, request, xp_points_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        xp_points = get_object_or_404(XpPoints, pk=xp_points_id)
        # allow superuser or user who is the owner of the xp_points to view the xp_points
        # if not user.is_superuser and user != xp_points.user:
        #     return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(xp_points)
        return Response(serializer.data)

    def patch(self, request, xp_points_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        xp_points = get_object_or_404(XpPoints, pk=xp_points_id)

        points = request.data.get('points')
        if points:
            xp_points.points = points
        exp = request.data.get('exp')
        if exp:
            xp_points.exp = exp
        level = request.data.get('level')
        if level:
            xp_points.level = level
        
        xp_points.save()
        serializer = self.get_serializer(xp_points)
        return Response(serializer.data)

    def delete(self, request, xp_points_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        xp_points = get_object_or_404(XpPoints, pk=xp_points_id)
        xp_points.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
