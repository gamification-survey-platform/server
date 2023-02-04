from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible

from app.gamification.models.entity import Team

from .user import CustomUser
from .registration import Registration

@deconstructible
class FileSizeValidator:
    '''
    Validates the size of a file.
    '''
    messages = {
        'max_size': _('The file must be smaller than %(max_size)s.'),
        'min_size': _('The file must be larger than %(min_size)s.'),
    }

    def __init__(self, max_size=None, min_size=None):
        self.max_size = max_size
        self.min_size = min_size

    def __call__(self, value):
        if self.max_size is not None and value.size > self.max_size:
            raise ValidationError(
                self.messages['max_size'],
                code='max_size',
                params={'max_size': self._normalize_size(self.max_size)},
            )
        if self.min_size is not None and value.size < self.min_size:
            raise ValidationError(
                self.messages['min_size'],
                code='min_size',
                params={'min_size': self._normalize_size(self.min_size)},
            )

    def _normalize_size(self, size):
        if size / 1024 / 1024 / 1024 >= 1:
            return f'{size / 1024 / 1024 / 1024:.0f}GB'
        if size / 1024 / 1024 >= 1:
            return f'{size / 1024 / 1024:.0f}MB'
        if size / 1024 >= 1:
            return f'{size / 1024:.0f}KB'

        return f'{size:.0f}B'

class Course(models.Model):

    course_number = models.CharField(
        _('course number'), max_length=150, blank=True)

    course_name = models.CharField(
        _('course name'), max_length=150, blank=True)

    syllabus = models.TextField(_('syllabus'), blank=True)

    semester = models.CharField(_('semester'), max_length=150, blank=True)

    visible = models.BooleanField(_('visible'), default=False)

    users = models.ManyToManyField(CustomUser, through='Registration')

    image_extension_validator = FileExtensionValidator(
        allowed_extensions=['png', 'jpg', 'jpeg'])
    file_size_validator = FileSizeValidator(max_size=1024 * 1024 * 5)

    picture = models.ImageField(
        _('course picture'),
        upload_to='profile_pics',
        blank=True,
        validators=[image_extension_validator, file_size_validator],
    )

    class Meta:
        db_table = 'courses'
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    def get_query(self, role):
        return Registration.objects.filter(
            courses=self.pk, userRole=role).values_list('users', flat=True)

    @property
    def instructors(self):
        query = self.get_query(Registration.UserRole.Instructor)
        return self.users.filter(pk__in=query)

    @property
    def students(self):
        query = self.get_query(Registration.UserRole.Student)
        return self.users.filter(pk__in=query)

    @property
    def TAs(self):
        query = self.get_query(Registration.UserRole.TA)
        return self.users.filter(pk__in=query)

    @property
    def teams(self):
        return Team.objects.filter(course=self)

    def get_course_name(self):
        '''Return the course name.'''
        return self.course_name

    def __str__(self):
            return f'{self.course_name + " - " + self.course_number}'


