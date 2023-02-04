from django.db import models
from django.utils.translation import gettext_lazy as _
from app.gamification.models.membership import Membership


class Entity(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    registration = models.ManyToManyField('Registration', through='Membership')

    class Meta:
        db_table = 'entities'
        verbose_name = _('entity')
        verbose_name_plural = _('entities')

    @property
    def members(self):
        membership = Membership.objects.filter(entity=self.pk)
        students = [e.student.users for e in membership]
        return students

    @property
    def number_members(self):
        membership = Membership.objects.filter(entity=self.pk)
        students = [e.student.users for e in membership]
        return len(students)


class Individual(Entity):

    class Meta():
        db_table = 'individuals'
        verbose_name = _('individual')
        verbose_name_plural = _('individuals')


class Team(Entity):
    name = models.CharField(_('team'), max_length=150, blank=True)

    class Meta():
        db_table = 'teams'
        verbose_name = _('team')
        verbose_name_plural = _('teams')

    def __str__(self):
        return f'{self.name}'
