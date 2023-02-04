from django.db import models


class QuestionOption(models.Model):
    """
    Model for QuestionOption
    """
    question = models.ForeignKey('Question', on_delete=models.CASCADE)

    option_choice = models.ForeignKey('OptionChoice', on_delete=models.CASCADE)

    number_of_text = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'question_option'
        verbose_name = 'question option'
        verbose_name_plural = 'question options'
