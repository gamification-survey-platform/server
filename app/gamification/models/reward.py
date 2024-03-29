from django.db import models
from django.utils.translation import gettext_lazy as _

from app.gamification.models.course import Course
from app.gamification.models.user_reward import UserReward


class Reward(models.Model):
    class RewardType(models.TextChoices):
        OTHER = "Other"
        LATE_SUBMISSION = "Late Submission"
        BONUS = "Bonus"

    name = models.CharField(_("name"), max_length=255, default="", blank=False)
    description = models.TextField(_("description"), default="", blank=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    points = models.IntegerField(_("points"), default=0, null=True, blank=False)
    reward_type = models.TextField(choices=RewardType.choices, default=RewardType.OTHER)
    inventory = models.IntegerField(_("inventory"), default=-1, null=True, blank=True)
    is_active = models.BooleanField(_("is active"), default=False, null=True, blank=True)
    picture = models.ImageField(_("reward_picture"), upload_to="rewards", null=True, blank=True)
    quantity = models.IntegerField(_("quantity"), null=True, blank=True)

    class Meta:
        db_table = "rewards"
        verbose_name = _("reward")
        verbose_name_plural = _("rewards")

    @property
    def active(self):
        self.is_active = True
        self.save()

    @property
    def inactive(self):
        self.is_active = False
        self.save()

    @property
    def owners(self):
        owners = UserReward.objects.filter(reward=self)
        return list(owners)
