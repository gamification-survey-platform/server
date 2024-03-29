from django.db import models
from django.utils.translation import gettext_lazy as _

from app.gamification.models.course import Course
from app.gamification.models.survey import FeedbackSurvey


class Assignment(models.Model):
    class AssigmentType(models.TextChoices):
        Individual = "Individual"
        Team = "Team"

    class SubmissionType(models.TextChoices):
        File = "File"
        URL = "URL"
        Text = "Text"

    class ReviewerAssignPolicy(models.TextChoices):
        A = "A"
        B = "B"
        C = "C"

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    assignment_name = models.CharField(_("assignment name"), max_length=150, blank=True)

    description = models.TextField(_("description"), blank=True)

    assignment_type = models.TextField(choices=AssigmentType.choices, default=AssigmentType.Individual, blank=True)

    submission_type = models.TextField(choices=SubmissionType.choices, default=SubmissionType.File, blank=True)

    total_score = models.FloatField(null=True, blank=True)

    weight = models.FloatField(null=True, blank=True)

    date_released = models.DateTimeField(_("date released"), null=True, blank=True)

    date_due = models.DateTimeField(_("date due"), null=True, blank=True)

    review_assign_policy = models.TextField(
        choices=ReviewerAssignPolicy.choices, default=ReviewerAssignPolicy.A, blank=True
    )
    
    min_reviewers = models.IntegerField(null=True, default=2, blank=True)

    ipsatization_min = models.IntegerField(null=True, default=80, blank=True)

    ipsatization_max = models.IntegerField(null=True, default=100, blank=True)

    class Meta:
        db_table = "assignment"
        verbose_name = _("assignment")
        verbose_name_plural = _("assignments")

    @property
    def survey(self):
        feedback_survey = FeedbackSurvey.objects.filter(assignment=self)
        if len(feedback_survey) > 0:
            feedback_survey = feedback_survey.order_by('id').last()
            return feedback_survey
        else:
            return None

    @property
    def feedback_survey(self):
        feedback_survey = FeedbackSurvey.objects.filter(assignment=self)
        if len(feedback_survey) > 0:
            feedback_survey = feedback_survey[0]
            return feedback_survey
        else:
            return None

    def __str__(self):
        return f"{self.assignment_name}"
