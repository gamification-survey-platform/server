from django.db import models
from django.utils.translation import gettext_lazy as _

from .entity import Individual, Team
from .user import CustomUser


class Registration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    course = models.ForeignKey("Course", on_delete=models.CASCADE)

    points = models.IntegerField(_("points"), default=0, null=True, blank=False)

    course_experience = models.IntegerField(_("points"), default=0, null=True, blank=False)

    class Meta:
        db_table = "registration"
        verbose_name = _("registration")
        verbose_name_plural = _("registrations")

    def __str__(self):
        return f"{self.course.course_name} - {self.user.andrew_id}"

    @property
    def team(self):
        try:
            return Team.objects.get(registration=self)
        except Team.DoesNotExist:
            return None

    @property
    def individual(self):
        try:
            return Individual.objects.get(registration=self)
        except Individual.DoesNotExist:
            return None
