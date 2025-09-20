# hr_system/settings.py
from pathlib import Path
import os
from decouple import config
import dj_database_url
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# -------------------
# Applications
# -------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps
    'accounts',
    'salaries',
    'rest_framework',
    'rest_framework.authtoken',
    'tokens',
    'advances',
    'loans.apps.LoansConfig',
    'axes',   # مضافة من نسخة اللوكال
]

AUTH_USER_MODEL = 'accounts.CustomUser'

# -------------------
# Middleware
# -------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'axes.middleware.AxesMiddleware',  # مضافة من نسخة اللوكال
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.TokenExpirationMiddleware',
]

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # أو AxesBackend
    'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'hr_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "salaries" / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hr_system.wsgi.application'

# -------------------
# Database
# -------------------
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=f"postgres://postgres:123@localhost:5432/mysales")
    )
}

# -------------------
# Password validation
# -------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------
# Internationalization
# -------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

# -------------------
# Static & Media
# -------------------
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------
# CSRF & Cookies
# -------------------
CSRF_TRUSTED_ORIGINS = [
    'https://salary.el-aseel.com',
    'https://salary1.el-aseel.com',
    'https://r8sc880g8s8w4oo8g4c4o4og.41.196.0.92.sslip.io',
]

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Lax'

# -------------------
# REST Framework
# -------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'accounts.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'accounts.exceptions.custom_exception_handler',
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
    'DATE_FORMAT': "%Y-%m-%d",
}

# -------------------
# Token Expiry
# -------------------
TOKEN_EXPIRE_TIME = 3600  # ثانية (ساعة واحدة)

# -------------------
# Axes Config
# -------------------
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 15
AXES_COOLOFF_TIME = timedelta(hours=1)
AXES_ONLY_USER_FAILURES = False
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = 'account_locked.html'
