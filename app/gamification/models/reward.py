from django.db import models
from django.utils.translation import gettext_lazy as _
from app.gamification.models.course import Course


class Reward(models.Model):
    class RewardType(models.TextChoices):
        Badge = 'Badge'
        Bonus = 'Bonus'
        lateSubmission = 'Late Submission'
        theme = 'Theme'
        other = 'Other'

    class Theme(models.TextChoices):
        dark = 'Dark'
        red = 'Red'

    name = models.CharField(_('name'), max_length=255, default='', blank=False)
    description = models.TextField(_('description'), default='', blank=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=0)
    exp_point = models.IntegerField(
        _('exp_point'), default=0, null=True, blank=False)
    type = models.TextField(
        choices=RewardType.choices, default=RewardType.other, blank=False)
    inventory = models.IntegerField(
        _('inventory'), default=-1, null=True, blank=True)
    is_active = models.BooleanField(
        _('is active'), default=False, null=True, blank=True)
    picture = models.ImageField(
        _('reward_picture'), upload_to='rewards', null=True, blank=True)
    quantity = models.IntegerField(
        _('quantity'),  null=True, blank=True)
    theme = models.TextField(
        choices=Theme.choices, null=True, blank=True)

    class Meta:
        db_table = 'rewards'
        verbose_name = _('reward')
        verbose_name_plural = _('rewards')

    @property
    def active(self):
        self.is_active = True
        self.save()

    @property
    def inactive(self):
        self.is_active = False
        self.save()
