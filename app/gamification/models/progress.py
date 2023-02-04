from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class Progress(models.Model):
    met = models.BooleanField(default=False)
    cur_point = models.FloatField(default=0, blank=True)
    constraint = models.ForeignKey('Constraint', on_delete=models.CASCADE)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)

    class Meta:
        db_table = 'progresses'
        verbose_name = _('progress')
        verbose_name_plural = _('progresses')

