from django.db import models

from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question_option import QuestionOption


class Question(models.Model):
    """
    Model for Question
    """
    class QuestionType(models.TextChoices):
        MULTIPLETEXT = 'MULTIPLETEXT'
        FIXEDTEXT = 'FIXEDTEXT'
        MULTIPLECHOICE = 'MULTIPLECHOICE'
        SLIDEREVIEW = 'SLIDEREVIEW'
        TEXTAREA = 'TEXTAREA'
        NUMBER = 'NUMBER'
        SCALEMULTIPLECHOICE = 'SCALEMULTIPLECHOICE'

    section = models.ForeignKey('SurveySection', on_delete=models.CASCADE)

    text = models.TextField(blank=True)

    is_required = models.BooleanField(default=False)

    is_multiple = models.BooleanField(default=False)

    is_template = models.BooleanField(default=False)

    dependent_question = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)

    question_type = models.TextField(
        choices=QuestionType.choices, default=QuestionType.MULTIPLECHOICE)

    option_choices = models.ManyToManyField(
        'OptionChoice', through='QuestionOption')

    number_of_scale = models.IntegerField(default=5, null=True, blank=True)

    class Meta:
        db_table = 'question'
        verbose_name = 'question'
        verbose_name_plural = 'questions'

    @property
    def options(self):
        return QuestionOption.objects.filter(question=self).order_by('pk')
