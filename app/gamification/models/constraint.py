from django.db import models
from django.utils.translation import gettext_lazy as _


class Constraint(models.Model):
    url = models.TextField(_('url'), blank=True)
    threshold = models.IntegerField()
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = 'constraints'
        verbose_name = _('constraint')
        verbose_name_plural = _('constraints')


class Point(Constraint):

    class Meta:
        db_table = 'points'
        verbose_name = _('point')
        verbose_name_plural = _('points')


class Action(Constraint):
    
    class Meta:
        db_table = 'actions'
        verbose_name = _('action')
        verbose_name_plural = _('actions')
