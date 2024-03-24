from django.db import models
from app.gamification.models.trivia import Trivia
from app.gamification.models.user import CustomUser
from django.utils.translation import gettext_lazy as _

class UserTrivia(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    trivia = models.ForeignKey(Trivia, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = "user_trivia"
        verbose_name = "user trivia"
        verbose_name_plural = "user trivia"
        unique_together = ('user', 'trivia')