"""
Local (development) settings for config project.
Inherits everything from base.py and overrides dev-specific values.
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
# This key is fine for local development only — never reuse in production.
SECRET_KEY = 'django-insecure-f7#lxl&z^ut3^k0za(=(d7mb9!ulx3yri9f-*=9@5$g%!k^r8d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']