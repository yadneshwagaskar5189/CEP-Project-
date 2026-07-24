"""
Django settings for the Healthcare Awareness & Literacy Platform.
Community Engagement Project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: change this before deploying anywhere public.
SECRET_KEY = "django-insecure-change-me-for-production-cep-healthcare-2026"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Project apps
    "core",
    "schemes",
    "hospitals",
    "prediction",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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
                "core.context_processors.site_info",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-in"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Project specific -------------------------------------------------------
ML_MODEL_PATH = BASE_DIR / "ml_model" / "disease_model.pkl"
ML_META_PATH = BASE_DIR / "ml_model" / "model_meta.json"

SITE_NAME = "Arogya Disha"
SITE_TAGLINE = "Healthcare Awareness & Literacy Platform"
EMERGENCY_NUMBER = "108"

# Lab-report photos are read and thrown away inside the request that uploads
# them. Django spills any upload over 2.5 MB to a temporary file on disk by
# default, which would quietly make the promise shown on the upload page false,
# so the threshold is raised past the 12 MB the view accepts.
FILE_UPLOAD_MAX_MEMORY_SIZE = 13 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 13 * 1024 * 1024

# Admin branding
ADMIN_SITE_HEADER = "Arogya Disha - Control Panel"
