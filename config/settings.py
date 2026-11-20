"""
JIFUNZE AI - Django settings
Open Learning Intelligence
"""
import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-key-replace-me")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    # JIFUNZE AI core apps
    "apps.accounts.apps.AccountsConfig",
    "apps.institutions.apps.InstitutionsConfig",
    "apps.resources.apps.ResourcesConfig",
    "apps.learning.apps.LearningConfig",
    "apps.teacher_studio.apps.TeacherStudioConfig",
    "apps.governance.apps.GovernanceConfig",
    "apps.ai_gateway.apps.AiGatewayConfig",
    "apps.audit.apps.AuditConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
# Database - SQLite for Day 1 local development. PostgreSQL from Day 2 onward.
import os
from dotenv import load_dotenv
load_dotenv()
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
if os.getenv("USE_POSTGRES") == "True":
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "jifunze"),
        "USER": os.getenv("POSTGRES_USER", "jifunze_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "jifunze_password"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}
# PostgreSQL + pgvector configuration (uncomment to use with docker-compose)
# import os
# if os.getenv('USE_POSTGRES') == 'True':
#     DATABASES['default'] = {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('POSTGRES_DB', 'jifunze'),
#         'USER': os.getenv('POSTGRES_USER', 'jifunze_user'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'jifunze_password'),
#         'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
#         'PORT': os.getenv('POSTGRES_PORT', '5432'),
#     }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
# Internationalisation
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True
# Static and media
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# Custom user model - must be set before first migration
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "admin:login"
LOGIN_REDIRECT_URL = "/admin/"
# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
# AI Gateway configuration (no provider wired yet - Day 5)
AI_PROVIDER = os.getenv("AI_PROVIDER", "none")
AI_MODEL = os.getenv("AI_MODEL", "")
AI_API_KEY = os.getenv("AI_API_KEY", "")
# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}


