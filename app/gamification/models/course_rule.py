from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class CourseRule(models.Model):
    rule = models.ForeignKey('Rule', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    class Meta:
        db_table = 'course_rules'
        verbose_name = _('course rule')
        verbose_name_plural = _('course_rules')
