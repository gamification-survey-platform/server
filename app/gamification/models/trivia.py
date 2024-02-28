from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _


class Trivia(models.Model):
    question = models.TextField(blank=True)
    answer = models.TextField(blank=True)
    hints = ArrayField(models.TextField(blank=True))
    course = models.ForeignKey("Course", on_delete=models.CASCADE)

    class Meta:
        db_table = "trivia"
        verbose_name = _("trivia")
        verbose_name_plural = _("trivias")
