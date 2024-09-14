# ruff: noqa: F405
import os

from .base import *  # noqa: F403

try:
    from .dev import *  # noqa
except ImportError:
    pass

SECURE_SSL_REDIRECT  = False
CSRF_TRUSTED_ORIGINS = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "http://*.localhost").split(",")