from django.db import models
from django.utils.translation import gettext_lazy as _
from app.gamification.models.course import Course


class RewardType(models.Model):
    type = models.CharField(_('type'), max_length=255, default='', blank=False)

    class Meta:
        db_table = 'reward_type'
        verbose_name = _('reward type')
        verbose_name_plural = _('reward types')

    def __str__(self):
        return self.type

    @property
    def valid_type(self):
        return self.type in ['Bonus', 'Late Submission', 'Other']
