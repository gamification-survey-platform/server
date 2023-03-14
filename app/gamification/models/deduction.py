from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class Deduction(models.Model):

    grade = models.ForeignKey('Grade', on_delete=models.CASCADE)

    deduction_score = models.IntegerField(null=True, blank=True)
    
    title = models.CharField(_('title'), max_length=150, blank=True)
    
    description = models.TextField(_('description'), blank=True)
    
    timestamp = models.DateTimeField(
        _('update time'), null=True, default=now, blank=True)

    class Meta:
        db_table = 'deduction'
        verbose_name = _('deduction')
        verbose_name_plural = _('deductions')
