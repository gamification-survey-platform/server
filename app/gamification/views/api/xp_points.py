from app.gamification.models.xp_points import XpPoints
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from app.gamification.models.user import CustomUser
from app.gamification.models.behavior import Behavior
from app.gamification.models.exp_history import ExpHistory
from app.gamification.utils import get_user_pk, ASSIGNMENT_POINTS, SURVEY_POINTS, level_func
from app.gamification.serializers.xp_points import XpPointsSerializer
from django.shortcuts import get_object_or_404
from app.gamification.models.xp_points import XpPoints


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
            xp_points.exp_points = points
            xp_points.exp = exp
            xp_points.level = level
            xp_points.save()
            serializer = self.get_serializer(xp_points)
            return Response(serializer.data, status=status.HTTP_200_OK)

        xp_points = XpPoints.objects.create(
            user=user,
            exp_points=points,
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

        points = request.data.get('exp_points')
        if points:
            xp_points.exp_points = points
        exp = request.data.get('exp')
        if exp:
            xp_points.exp = int(exp)
            # upgrade if exp is enough, level up for every 1000 exp
            cur_level = xp_points.level
            if xp_points.exp >= 1000:
                cur_level += 1
                xp_points.exp -= 1000
                xp_points.level = cur_level

        # also allow staff to manually change level if needed
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


class UpdateExp(generics.RetrieveUpdateAPIView):
    queryset = XpPoints.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = XpPointsSerializer

    def patch(self, request, *args, **kwargs):
        user_id = get_user_pk(request)
        user = CustomUser.objects.get(pk=user_id)
        opeartion = request.data.get('opeartion')
        method = request.data.get('method')
        api = request.data.get('api')

        # check if user has already gained exp by this operation
        try:
            exp_history = ExpHistory.objects.get(
                user=user, method=method, api=api)
            return Response(data={'messages': 'you have already gained exp by this operation'}, status=status.HTTP_400_BAD_REQUEST)
        # if not, update the exp and create a new exp history
        except ExpHistory.DoesNotExist:
            exp_history = ExpHistory.objects.create(
                user=user, method=method, api=api)
            exp_history.save()
        try:
            behavior = Behavior.objects.get(opeartion=opeartion)
        except Behavior.DoesNotExist:
            return Response(data={'messages': 'behavior not found'}, status=status.HTTP_400_BAD_REQUEST)
        points = behavior.points
        try:
            xp_points = XpPoints.objects.get(user=user)
        except XpPoints.DoesNotExist:
            xp_points = XpPoints.objects.create(user=user)
        xp_points.exp_points += points
        required_exp = level_func(xp_points.level)
        if xp_points.exp + points >= required_exp:
            xp_points.level += 1
            xp_points.exp = xp_points.exp + points - required_exp
        else:
            xp_points.exp += points
        xp_points.save()
        serializer = self.get_serializer(xp_points)
        data = serializer.data
        data["opeartion"] = opeartion
        return Response(data)
