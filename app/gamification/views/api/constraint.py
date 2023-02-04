from app.gamification.models.achievement import Achievement
from app.gamification.models.constraint import Constraint
from app.gamification.models.progress import Progress
from app.gamification.models.rule import Rule
from app.gamification.models.rule_constraint import RuleConstraint
from app.gamification.models.user_reward import UserReward
from app.gamification.serializers.constraint import ConstraintSerializer, ProgressSerializer
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import permissions
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

class ConstraintList(generics.ListCreateAPIView):
    queryset = Constraint.objects.all()
    serializer_class = ConstraintSerializer
    # permission_classes = [IsAdminOrReadOnly]

class ConstraintDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Constraint.objects.all()
    serializer_class = ConstraintSerializer
    # permission_classes = [permissions.IsAdminUser]

    def get(self, request, url, *args, **kwargs):
        constraint = get_object_or_404(Constraint, url=url)
        serializer = self.get_serializer(constraint)
        return Response(serializer.data)

    def put(self, request, url, *args, **kwargs):
        constraint = get_object_or_404(Constraint, url=url)
        threshold = request.data.get('threshold')
        
        constraint.threshold = threshold
        constraint.save()
        serializer = self.get_serializer(constraint)
        return Response(serializer.data)

    def delete(self, request, url, *args, **kwargs):
        constraint = get_object_or_404(Constraint, url=url)
        constraint.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ConstraintProgress(generics.ListAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, url, *args, **kwargs):
        constraint = get_object_or_404(Constraint, url=url)
        progress = Progress.objects.filter(constraint=constraint)
        serializer = self.get_serializer(progress, many=True)
        return Response(serializer.data)


def track_progress(user, progress, constraint):
    if progress.cur_point >= constraint.threshold:
        progress.met = True
        progress.save()
        rule_constraints = RuleConstraint.objects.filter(constraint=constraint)
        for rule_constraint in rule_constraints:
            rule = rule_constraint.rule
            for rule_constraint in rule.rule_constraints:
                cur_progress = get_object_or_404(Progress, user=user, constraint=rule_constraint.constraint)
                if not cur_progress.met:
                    return progress
            rewards = rule.rewards
            for reward in rewards:
                if UserReward.objects.filter(user=user, reward=reward).count() == 0:
                    user_reward = UserReward(user=user, reward=reward)
                    user_reward.save()
    return progress

class ActionConstraintProgressDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    # permission_classes = [permissions.IsAdminUser]

    def get(self, request, url, *args, **kwargs):
        constraint = get_object_or_404(Constraint, url=url)
        user = request.user
        progress = get_object_or_404(Progress, constraint=constraint, user=user)
        serializer = self.get_serializer(progress)
        return Response(serializer.data)

    def put(self, request, url, *args, **kwargs):
        constraint = get_object_or_404(Constraint, url=url)
        user = request.user
        if Progress.objects.filter(constraint=constraint, user=user).count() == 0:
            progress = Progress(constraint=constraint, user=user)
        else:
            progress = get_object_or_404(Progress, constraint=constraint, user=user)
        progress.cur_point = progress.cur_point + 1
        progress.save()
        progress = track_progress(user, progress, constraint)
        serializer = self.get_serializer(progress)
        return Response(serializer.data)

    def delete(self, request, url, *args, **kwargs):
        constraint = get_object_or_404(Constraint, url=url)
        user = request.user
        progress = get_object_or_404(Progress, constraint=constraint, user=user)
        progress.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GradeConstraintProgressDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    # permission_classes = [permissions.IsAdminUser]

    def get(self, request, url, *args, **kwargs):
        constraint = get_object_or_404(Constraint, url=url)
        user = request.user
        progress = get_object_or_404(Progress, constraint=constraint, user=user)
        serializer = self.get_serializer(progress)
        return Response(serializer.data)

    def put(self, request, url, *args, **kwargs):
        constraint = get_object_or_404(Constraint, url=url)
        user = request.user
        if Progress.objects.filter(constraint=constraint, user=user).count() == 0:
            progress = Progress(constraint=constraint, user=user)
        else:
            progress = get_object_or_404(Progress, constraint=constraint, user=user)
        progress.cur_point = max(int(request.data.get('cur_point')), progress.cur_point)
        progress.save()
        progress = track_progress(user, progress, constraint)
        serializer = self.get_serializer(progress)
        return Response(serializer.data)

    def delete(self, request, url, *args, **kwargs):
        constraint = get_object_or_404(Constraint, url=url)
        user = request.user
        progress = get_object_or_404(Progress, constraint=constraint, user=user)
        progress.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    