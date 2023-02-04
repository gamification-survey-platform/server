from .default import *


# Override the 'DATABASES' settings in default.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
}

MEDIA_ROOT = BASE_DIR / 'app/gamification/tests/media'
