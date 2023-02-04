from rest_framework import generics , status
from rest_framework import permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from app.gamification.models.achievement import Achievement
from app.gamification.models.constraint import Constraint
from app.gamification.models.progress import Progress
from app.gamification.models.rule import Rule
from app.gamification.models.rule_constraint import RuleConstraint
from app.gamification.models.user_reward import UserReward
from app.gamification.serializers.constraint import ConstraintSerializer, ProgressSerializer
from app.gamification.serializers.rule import RuleSerializer

# get all progress for all rules
# getAllRuleProgress_data = 
# [
# 	{
#   rule_name: string,
# 	conditions: [
#       { 
# 		    url: string,
# 		    Curr_count: int,
# 		    Unlock_count: int,
# 		},
#       ]
#   },
# ]

class getAllRules(generics.ListAPIView):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    # permission_classes = [IsAdminOrReadOnly]

class getAllRuleProgress(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rule.objects.all()
    rules = Rule.objects.all()
    Constraints = Constraint.objects.all()
    serializer_class = RuleSerializer
    def get(self, request, *args, **kwargs):
        # get all progress for all rules
        user = request.user
        getAllRuleProgress_data = []
        for rule in self.rules:
            rule_data = {}
            rule_data['rule_name'] = rule.name
            rule_data['description'] = rule.description
            rule_data['conditions'] = []
            rule_constraints = RuleConstraint.objects.filter(rule=rule)
            for rule_constraint in rule_constraints:
                constraint = rule_constraint.constraint
                progresses = Progress.objects.filter(user=user, constraint=constraint)
                for progress in progresses:
                    rule_data['conditions'].append({
                        'url': constraint.url,
                        'Curr_count': progress.cur_point,
                        'description': constraint.description,
                        'Unlock_count': constraint.threshold,
                    })
            getAllRuleProgress_data.append(rule_data)
        # remove rules that have empty conditions
        for rule in getAllRuleProgress_data:
            if len(rule['conditions']) == 0:
                getAllRuleProgress_data.remove(rule)
        return Response(getAllRuleProgress_data)
    
    
class getRulesProgressByContraint(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rule.objects.all()
    rules = Rule.objects.all()
    Constraints = Constraint.objects.all()
    serializer_class = RuleSerializer
    def get(self, request, constraint_pk, *args, **kwargs):
        # get all progress for all rules
        user = request.user
        getAllRuleProgress_data = []
        for rule in self.rules:
            rule_data = {}
            rule_data['rule_name'] = rule.name
            rule_data['conditions'] = []
            rule_constraints = RuleConstraint.objects.filter(rule=rule)
            if constraint_pk not in [rule_constraints.constraint.pk for rule_constraints in rule_constraints]:
                continue
            for rule_constraint in rule_constraints:
                constraint = rule_constraint.constraint
                progresses = Progress.objects.filter(user=user, constraint=constraint)
                for progress in progresses:
                    rule_data['conditions'].append({
                        'url': constraint.url,
                        'description': constraint.description,
                        'Curr_count': progress.cur_point,
                        'Unlock_count': constraint.threshold,
                    })
            getAllRuleProgress_data.append(rule_data)

        return Response(getAllRuleProgress_data)