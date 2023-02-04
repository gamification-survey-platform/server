from django.db import models
from django.utils.translation import gettext_lazy as _


class RuleConstraint(models.Model):
    rule = models.ForeignKey('Rule', on_delete=models.CASCADE)
    constraint = models.ForeignKey('Constraint', on_delete=models.CASCADE)

    class Meta:
        db_table = 'rule_constraints'
        verbose_name = _('rule constraint')
        verbose_name_plural = _('rule constraints')
