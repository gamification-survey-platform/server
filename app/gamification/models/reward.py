from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class Reward(models.Model):
    description = models.TextField(_('description'), blank=True)
    rule = models.ForeignKey('Rule', on_delete=models.CASCADE)

    class Meta:
        db_table = 'rewards'
        verbose_name = _('reward')
        verbose_name_plural = _('rewards')

