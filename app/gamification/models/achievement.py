from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class Achievement(models.Model):
    student = models.ForeignKey('Registration', on_delete=models.CASCADE)
    rule = models.ForeignKey('Rule', on_delete=models.CASCADE)

    class Meta:
        db_table = 'achievements'
        verbose_name = _('achievement')
        verbose_name_plural = _('achievements')

