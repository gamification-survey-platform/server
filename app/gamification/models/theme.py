from django.db import models
from django.utils.translation import gettext_lazy as _


class Theme(models.Model):
    colorBgBase = models.CharField(_("Background color"), max_length=7, blank=True)

    colorTextBase = models.CharField(_("Text color"), max_length=7, blank=True)

    colorPrimary = models.CharField(_("Primary color"), max_length=7, blank=True)

    colorSuccess = models.CharField(_("Success color"), max_length=7, blank=True)

    colorWarning = models.CharField(_("Warning color"), max_length=7, blank=True)

    colorError = models.CharField(_("Error color"), max_length=7, blank=True)

    cursor = models.CharField(_("Cursor"), max_length=15, blank=True)

    class Meta:
        db_table = "theme"
        verbose_name = "theme"
        verbose_name_plural = "theme"
