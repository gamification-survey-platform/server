from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from .user import CustomUser


class ExpHistory(models.Model):
    class methodEnum(models.TextChoices):
        GET = 'GET'
        POST = 'POST'
        PATCH = 'PATCH'
        DELETE = 'DELETE'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    method = models.TextField(
        choices=methodEnum.choices, default=methodEnum.GET)

    api = models.TextField(_('api'), default='', blank=False)

    class Meta:
        db_table = 'exp_history'
        verbose_name = _('exp history')
        verbose_name_plural = _('exp histories')
