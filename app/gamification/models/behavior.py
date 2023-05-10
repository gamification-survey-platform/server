from django.db import models
from django.utils.translation import gettext_lazy as _


class Behavior(models.Model):
    class methodEnum(models.TextChoices):
        GET = "GET"
        POST = "POST"
        PATCH = "PATCH"
        DELETE = "DELETE"

    # fields for customizing behavior points

    # method = models.TextField(
    #     choices=methodEnum.choices, default=methodEnum.GET)

    # api = models.TextField(_('api'), default='', blank=False)

    operation = models.TextField(_("operation"), default="", blank=False)

    points = models.IntegerField(_("points"), default=0, null=True, blank=False)

    class Meta:
        db_table = "behaviors"
        verbose_name = _("behaviors")
        verbose_name_plural = _("behaviors")
