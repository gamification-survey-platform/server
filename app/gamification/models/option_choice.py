from django.db import models


class OptionChoice(models.Model):
    text = models.TextField(blank=True)
    question = models.ForeignKey("Question", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "option_choice"
        verbose_name = "option choice"
        verbose_name_plural = "option choices"
