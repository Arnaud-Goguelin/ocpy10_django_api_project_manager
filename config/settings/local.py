from .base import *


DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# add swagger
INSTALLED_APPS += [
    'drf_spectacular',
]

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'SoftDesk API',
    'DESCRIPTION': 'Project management API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False, # create response schema on request, not in initial html template
    'CAMELIZE_NAMES': True,
}

# SQLite DB for dev
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Console email backend to test email in local
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

