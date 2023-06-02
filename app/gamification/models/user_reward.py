from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from app.gamification.models.user import CustomUser


class UserReward(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reward = models.ForeignKey("Reward", on_delete=models.CASCADE)
    fulfilled = models.BooleanField(_("reward fulfilled"), default=False, null=True, blank=True)
    date_purchased = models.DateTimeField(_("date purchased"), null=True, default=now, blank=True)

    class Meta:
        db_table = "user_reward"
        verbose_name = _("user reward")
        verbose_name_plural = _("user rewards")
