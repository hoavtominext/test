"""
Django settings for DjangoRestApi project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from dotenv import load_dotenv
from socket import gethostname, gethostbyname 

load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'em6vjaht_(7i#*vu4w#8x(q&532u@z6n!zp%7p1gf7n1(og7#0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', gethostname(), gethostbyname(gethostname()), os.getenv('DOMAIN_SERVER'), '52.194.206.226']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'health_check',  # required
    'health_check.db',  # stock Django health checkers
    'health_check.cache',
    'health_check.storage',
    'Auth',
    'Users',
    'Question',
    'Company',
    'Workshop',
    'Answer',
    'Csaplus24',
    'Department',
    'MailMagazine',
    'MeanvalueStddeviation',
    'EmailPostLearningContent',
    'crontab',
    'ScheduleCron',
    'rest_framework',  # API
    'django_rest_passwordreset',
    'oauth2_provider',  # OAuth2
    'import_export',
    'rest_framework_swagger',
    'corsheaders',
    'Middleware',
]

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    #'SCOPES': {'read': 'Read scope', 'write': 'Write scope', 'groups': 'Access to your groups'}
    'SCOPES': {'coacha_admin': 'Coacha Admin', 'admin': 'Admin scope', 'user': 'User scope'}
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',

    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',

}

MIDDLEWARE = [
    'Middleware.AccessLogMiddleware.Middleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]
CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'DjangoRestApi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'DjangoRestApi.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASES_NAME'),
        'USER': os.getenv('DATABASES_USER'),
        'PASSWORD': os.getenv('DATABASES_PASSWORD'),
        'HOST': os.getenv('DATABASES_HOST'),  # Or an IP Address that your DB is hosted on
        'PORT': os.getenv('DATABASES_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.getenv('TIME_ZONE','UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

APPEND_SLASH = False

EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS',False)
EMAIL_HOST = os.getenv('EMAIL_HOST','localhost')
EMAIL_PORT = os.getenv('EMAIL_PORT',25)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER','username')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD','password')

SWAGGER_SETTINGS = {
    'JSON_EDITOR': True,
}

AUTH_USER_MODEL='Users.User'

# App settings

# Log anonymous actions?
ACTIVITYLOG_ANONYMOUS = True

# Update last activity datetime in user profile. Needs updates for user model.
ACTIVITYLOG_LAST_ACTIVITY = True
LAST_ACTIVITY = True
# Only this methods will be logged
ACTIVITYLOG_METHODS = ('POST', 'GET')

# List of response statuses, which logged. By default - all logged.
# Don't use with ACTIVITYLOG_EXCLUDE_STATUSES
ACTIVITYLOG_STATUSES = (200, )

# List of response statuses, which ignores. Don't use with ACTIVITYLOG_STATUSES
# ACTIVITYLOG_EXCLUDE_STATUSES = (302, )

# URL substrings, which ignores
ACTIVITYLOG_EXCLUDE_URLS = ('/admin/activity_log/activitylog', )

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

IP_WHITELIST_COUNT = 20