from django.db import models
from django.utils.translation import gettext_lazy as _

from .user import CustomUser


class TodoList(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    text = models.CharField(max_length=200)

    due_date = models.DateTimeField(null=True, blank=True)

    type_name = models.CharField(max_length=200, default="Assignment")

    type_icon = models.CharField(max_length=100, default="fa-solid fa-book")

    mandatory = models.BooleanField(default=False)

    class Meta:
        db_table = 'todo_list'
        verbose_name = _('todo_list')
        verbose_name_plural = _('todo_lists')
