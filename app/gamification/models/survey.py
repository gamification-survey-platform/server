from django.db import models

from app.gamification.models.survey_section import SurveySection


class FeedbackSurvey(models.Model):
    """
    Model for FeedbackSurvey
    """

    assignment = models.ForeignKey("Assignment", null=True, blank=True, on_delete=models.SET_NULL)

    date_released = models.DateTimeField(null=True, blank=True)

    date_due = models.DateTimeField(null=True, blank=True)
    
    is_released = models.BooleanField(default=False)
    
    name = models.CharField(max_length=150, default="Default Survey")

    instructions = models.TextField(blank=True)
    
    user = models.ForeignKey("CustomUser", null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        db_table = "feedback_survey"
        verbose_name = "feedback survey"
        verbose_name_plural = "feedback surveys"
    
    @property
    def sections(self):
        return SurveySection.objects.filter(survey=self).order_by("pk")
