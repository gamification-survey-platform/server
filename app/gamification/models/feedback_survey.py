from django.db import models


class FeedbackSurvey(models.Model):
    """
    Model for FeedbackSurvey
    """
    template = models.ForeignKey('SurveyTemplate', on_delete=models.CASCADE)

    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE)

    date_created = models.DateTimeField(auto_now_add=True)

    date_released = models.DateTimeField(null=True, blank=True)

    date_due = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'feedback_survey'
        verbose_name = 'feedback survey'
        verbose_name_plural = 'feedback surveys'
