from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.forms',

    'bootstrap4',
    'django_htmx',
    
    'Core',
    'Customer',
    'Expenditure',
    'Owner',
    'Product',
    'Revenue',
    'Transaction',
    'Ledger',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'FillingStation.urls'
WSGI_APPLICATION = 'FillingStation.wsgi.application'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'extra_tags': 'FillingStation.templatetags.extra_tags',
            }
        },
    },
]

# FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# Django will search for static files from STATIC_URL
STATIC_URL = '/static/'
# Django will also look for static files from STATICFILES_DIRS (outside of app)
STATICFILES_DIRS = [
    BASE_DIR / 'static', # need to be exist
    # BASE_DIR / 'build/static' // for react
]
# The absolute path to the directory where collectstatic will collect static files for deployment.
STATIC_ROOT = BASE_DIR / 'static_root'

# -------------------- User uploaded files directory ----------------------------
MEDIA_URL = '/media/'
# During development, you can serve user-uploaded media files from MEDIA_ROOT
MEDIA_ROOT = BASE_DIR / 'media_root'
# After deploying production server, run command - collectstatic
# This will copy all files from your static folders into the STATIC_ROOT directory.
