from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from app.gamification.models.user import CustomUser


class XpPoints(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    # ponits are the main currency of the game, they are used to buy rewards
    points = models.IntegerField(default=0, null=True, blank=True)
    
    # exp is only used to level up
    exp = models.IntegerField(default=0, null=True, blank=True)
    
    level = models.IntegerField(default=0, null=True, blank=True)
    
    class Meta:
        db_table = 'xp_points'
        verbose_name = _('xp points')
        verbose_name_plural = _('xp points')

