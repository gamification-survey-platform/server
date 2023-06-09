from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

image_extension_validator = FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg"])


class Theme(models.Model):
    name = models.TextField(blank=True)

    is_published = models.BooleanField(default=False)

    creator = models.ForeignKey("CustomUser", related_name="+", blank=True, null=True, on_delete=models.DO_NOTHING)

    colorBgBase = models.CharField(_("Background color"), max_length=7, blank=True)

    colorTextBase = models.CharField(_("Text color"), max_length=7, blank=True)

    colorPrimary = models.CharField(_("Primary color"), max_length=7, blank=True)

    colorSuccess = models.CharField(_("Success color"), max_length=7, blank=True)

    colorWarning = models.CharField(_("Warning color"), max_length=7, blank=True)

    colorError = models.CharField(_("Error color"), max_length=7, blank=True)

    cursor = models.ImageField(
        _("cursor icon"),
        upload_to="theme/cursor",
        blank=True,
        validators=[image_extension_validator],
    )

    multiple_choice_item = models.ImageField(
        _("multiple choice item"),
        upload_to="theme/multiple_choice_item",
        blank=True,
        validators=[image_extension_validator],
    )

    multiple_choice_target = models.ImageField(
        _("multiple choice target"),
        upload_to="theme/multiple_choice_target",
        blank=True,
        validators=[image_extension_validator],
    )

    multiple_select_item = models.ImageField(
        _("multiple select item"),
        upload_to="theme/multiple_select_item",
        blank=True,
        validators=[image_extension_validator],
    )

    multiple_select_target = models.ImageField(
        _("multiple select target"),
        upload_to="theme/multiple_select_target",
        blank=True,
        validators=[image_extension_validator],
    )

    scale_multiple_choice_item = models.ImageField(
        _("scale multiple choice item"),
        upload_to="theme/scale_multiple_choice_item",
        blank=True,
        validators=[image_extension_validator],
    )

    scale_multiple_choice_target = models.ImageField(
        _("scale multiple choice target"),
        upload_to="theme/scale_multiple_choice_target",
        blank=True,
        validators=[image_extension_validator],
    )

    class Meta:
        db_table = "theme"
        verbose_name = "theme"
        verbose_name_plural = "theme"
