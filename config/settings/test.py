"""
Test settings for config project.
"""

from .base import *

SECRET_KEY = env("SECRET_KEY", default="test-secret-key-not-for-production")

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}