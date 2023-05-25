from django.db import models

from app.gamification.models.option_choice import OptionChoice


class Question(models.Model):
    """
    Model for Question
    """

    class QuestionType(models.TextChoices):
        MULTIPLETEXT = "MULTIPLETEXT"
        FIXEDTEXT = "FIXEDTEXT"
        MULTIPLECHOICE = "MULTIPLECHOICE"
        SLIDEREVIEW = "SLIDEREVIEW"
        TEXTAREA = "TEXTAREA"
        NUMBER = "NUMBER"
        SCALEMULTIPLECHOICE = "SCALEMULTIPLECHOICE"
        MULTIPLESELECT = "MULTIPLESELECT"

    section = models.ForeignKey("SurveySection", on_delete=models.CASCADE)

    text = models.TextField(blank=True)

    is_required = models.BooleanField(default=False)

    question_type = models.TextField(choices=QuestionType.choices, default=QuestionType.MULTIPLECHOICE)

    number_of_scale = models.IntegerField(default=5, null=True, blank=True)

    number_of_text = models.PositiveIntegerField(default=1)

    gamified = models.BooleanField(default=True)

    phrased_positively = models.BooleanField(default=True)

    class Meta:
        db_table = "question"
        verbose_name = "question"
        verbose_name_plural = "questions"

    @property
    def options(self):
        return OptionChoice.objects.filter(question=self).order_by("pk")
