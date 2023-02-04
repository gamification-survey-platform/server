from django.db import models

from app.gamification.models.survey_section import SurveySection


class SurveyTemplate(models.Model):
    """
    Model for SurveyTemplate
    """
    name = models.CharField(max_length=150)

    instructions = models.TextField(blank=True)

    is_template = models.BooleanField(default=False)

    other_info = models.TextField(blank=True)

    class Meta:
        db_table = 'survey_template'
        verbose_name = 'survey template'
        verbose_name_plural = 'survey templates'

    def __str__(self):
        return self.name

    @property
    def sections(self):
        return SurveySection.objects.filter(template=self).order_by('pk')
