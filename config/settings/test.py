from .base import *

SECRET_KEY = env("SECRET_KEY", default="test-secret-key-not-for-production")

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

SMS_BACKEND = "console"