from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from app.gamification.models.rule_constraint import RuleConstraint
from app.gamification.models.reward import Reward


class Rule(models.Model):
    default = models.BooleanField(default=False)
    name = models.CharField(
        _('Rule name'), max_length=150, blank=True)

    description = models.TextField(_('description'), blank=True)

    @property
    def rule_constraints(self):
        return RuleConstraint.objects.filter(rule=self)

    @property
    def rewards(self):
        return Reward.objects.filter(rule=self)

    class Meta:
        db_table = 'rules'
        verbose_name = _('rule')
        verbose_name_plural = _('rules')

    def __str__(self):
        return f'{self.name}'
