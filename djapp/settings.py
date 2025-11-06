from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
# from sentry_sdk.integrations.django import DjangoIntegration
# import sentry_sdk

# -------------------------------------------------------------------
# BASE SETTINGS
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["*"]

# -------------------------------------------------------------------
# INSTALLED APPS
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "djproject",  # ✅ Your Django app
]

# -------------------------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------------------------
MIDDLEWARE = [
    # "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ROOT_URLCONF = "djproject.urls"

# -------------------------------------------------------------------
# TEMPLATES
# -------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "djproject.wsgi.application"

# -------------------------------------------------------------------
# DATABASE
# -------------------------------------------------------------------
DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': "postgres",
            'USER': "postgres",
            'PASSWORD': "postgres",
            'HOST': "localhost",
            'PORT': 5432,
        }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# -------------------------------------------------------------------
# AUTHENTICATION
# -------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 1
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# -------------------------------------------------------------------
# REST FRAMEWORK
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
}

# -------------------------------------------------------------------
# STATIC / MEDIA
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "site_assets"]
STATIC_ROOT = BASE_DIR / "static_cdn" / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "static_cdn" / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "https://llr.pagemasterpro.site",
]
CORS_ALLOW_CREDENTIALS = True

# -------------------------------------------------------------------
# CELERY
# -------------------------------------------------------------------
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "django-cache"

# -------------------------------------------------------------------
# SENTRY
# -------------------------------------------------------------------
# SENTRY_DSN = os.getenv("SENTRY_DSN", "")
# if SENTRY_DSN:
#     sentry_sdk.init(
#         dsn=SENTRY_DSN,
#         integrations=[DjangoIntegration()],
#         traces_sample_rate=1.0,
#         send_default_pii=True,
#         environment=os.getenv("LLR_ENV", "local"),
#     )

# -------------------------------------------------------------------
# FASTAPI SYNC INFO (Optional Helper)
# -------------------------------------------------------------------
# If you want FastAPI to use Django ORM, your FastAPI main.py should contain:
# -------------------------------------------------------------------
# import os, django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djproject.settings")
# django.setup()
# -------------------------------------------------------------------
# Now FastAPI can import and use Django models directly
# -------------------------------------------------------------------
