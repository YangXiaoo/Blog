"""
Django settings for web project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import ConfigParser
import getpass
import tempfile

config = ConfigParser.ConfigParser()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
config.read(os.path.join(BASE_DIR, 'myweb.conf'))
KEY_DIR = os.path.join(BASE_DIR, 'keys')

AUTH_USER_MODEL = 'myweb.User'

# mail config
MAIL_ENABLE = config.get('mail', 'mail_enable')
EMAIL_HOST = config.get('mail', 'email_host')
EMAIL_PORT = config.get('mail', 'email_port')
EMAIL_HOST_USER = config.get('mail', 'email_host_user')
EMAIL_HOST_PASSWORD = config.get('mail', 'email_host_password')
EMAIL_USE_TLS = config.getboolean('mail', 'email_use_tls')
try:
    EMAIL_USE_SSL = config.getboolean('mail', 'email_use_ssl')
except ConfigParser.NoOptionError:
    EMAIL_USE_SSL = False
EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend' if EMAIL_USE_SSL else 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_TIMEOUT = 5

# ======== Log ==========
LOG_DIR = os.path.join(BASE_DIR, 'logs')
myweb_KEY_DIR = os.path.join(BASE_DIR, 'keys/role_keys')
KEY = config.get('base', 'key')
URL = config.get('base', 'url')
LOG_LEVEL = config.get('base', 'log')
IP = config.get('base', 'ip')
PORT = config.get('base', 'port')

# ======== Connect ==========
try:
    NAV_SORT_BY = config.get('connect', 'nav_sort_by') # ip
except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
    NAV_SORT_BY = 'ip' 

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%&gytros3@xgd8+*ifw8mvdqfn(2-oumafc^oz3=(ga&b&^m57'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0/8']


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_crontab',
    
    'bootstrapform',
    'myweb',
    'admin',
    'django_markdown',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'myweb.urls'

WSGI_APPLICATION = 'myweb.wsgi.application'


DEFAULT_CHARSET = 'UTF-8'
# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {}
if config.get('db', 'engine') == 'mysql': 
    DB_HOST = config.get('db', 'host')
    DB_PORT = config.getint('db', 'port')
    DB_USER = config.get('db', 'user')
    DB_PASSWORD = config.get('db', 'password')
    DB_DATABASE = config.get('db', 'database')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': DB_DATABASE,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    }
elif config.get('db', 'engine') == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': config.get('db', 'database'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai' # incorrect time_zone can cause time error

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# there can add cronjobs

# QQ login
CLIENT_ID = 101536906
CLIENT_KEY = 'e532c0b219544705d5'
REDIRECT_URL = 'http://yangxiao.online/qqconnect'