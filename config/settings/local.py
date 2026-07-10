"""
Local (development) settings for config project.
Inherits everything from base.py and overrides dev-specific values.
"""

from .base import *

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["127.0.0.1", "localhost"],
)

DATABASES = {
    "default": env.db("DATABASE_URL")
}