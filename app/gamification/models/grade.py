from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from .deduction import Deduction

class Grade(models.Model):

    artifact = models.ForeignKey('Artifact', on_delete=models.CASCADE)

    score = models.IntegerField(null=True, blank=True)
    
    timestamp = models.DateTimeField(
        _('update time'), null=True, default=now, blank=True)

    @property
    def deductions(self):
        return Deduction.objects.filter(grade=self)

    class Meta:
        db_table = 'grade'
        verbose_name = _('grade')
        verbose_name_plural = _('grades')
