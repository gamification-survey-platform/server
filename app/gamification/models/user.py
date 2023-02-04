from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, andrew_id, email, password, **extra_fields):
        '''
        Create and save a user with the given username, email, and password.
        '''
        if not andrew_id:
            raise ValueError('The given Andrew ID must be set')

        email = self.normalize_email(email)
        user = self.model(andrew_id=andrew_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, andrew_id, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(andrew_id, email, password, **extra_fields)

    def create_superuser(self, andrew_id, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(andrew_id, email, password, **extra_fields)


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


class CustomUser(AbstractBaseUser, PermissionsMixin):

    username_validator = ASCIIUsernameValidator()
    image_extension_validator = FileExtensionValidator(
        allowed_extensions=['png', 'jpg', 'jpeg'])
    file_size_validator = FileSizeValidator(max_size=1024 * 1024 * 5)

    andrew_id = models.CharField(
        _('Andrew ID'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Lower case letters only.'),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that andrew id already exists.'),
        },
    )
    image = models.ImageField(
        _('profile picture'),
        upload_to='profile_pics',
        blank=True,
        validators=[image_extension_validator, file_size_validator],
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('A user with that email already exists.'),
        },
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    )
    date_joined = models.DateTimeField(_('data joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'andrew_id'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'
        # db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def is_activated(self):
        return self.last_login is not None

    def get_full_name(self):
        '''
        Return the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def name_or_andrew_id(self):
        if self.first_name == '':
            return self.andrew_id
        else:
            full_name = '%s %s' % (self.first_name, self.last_name)
            return full_name.strip()

    def __str__(self):
        return f'{self.andrew_id}'

    def get_short_name(self):
        '''Return the short name for the user.'''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''Send an email to this user.'''
        send_mail(subject, message, from_email, [self.email], **kwargs)
