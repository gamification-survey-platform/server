from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        FEEDBACK_REQUEST = "FEEDBACK_REQUEST"
        FEEDBACK_RESPONSE = "FEEDBACK_RESPONSE"
        POKE = "POKE"

    sender = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    receiver = models.ForeignKey("CustomUser", related_name="+", on_delete=models.CASCADE)
    type = models.TextField(choices=NotificationType.choices, default=NotificationType.POKE, blank=True)
    text = models.TextField(_("text"), blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notifications"
        verbose_name = "notification"
        verbose_name_plural = "notifications"

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: ({self.type}) - {self.text}"
