"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+#+67ob=%sgrr&#_yk&n&8w9y-uiyq1o$^mfuc8rj$)ld1cj28'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*','hakys.pythonanywhere.com','shop.diablaroja.es']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'blog',
	'shop',
    'registration',
    'bootstrap_toolkit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'mysite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#dabases

'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
'''
DATABASES = {
     'default': {
        #'ENGINE': 'django.db.backends.mysql',
        'ENGINE': 'mysql.connector.django',
        'NAME': 'djangogirls',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '/', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '', # Set to empty string for default.
    },
    'wordpress_60': {
        #'ENGINE': 'django.db.backends.mysql',
        'ENGINE': 'mysql.connector.django',
        'NAME': 'wordpress_60',
        'USER': 'operadorweb',
        'PASSWORD': '48933206Gloria',
        'HOST': 'diablaroja.es', 
        'PORT': '3306', 
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': { 'min_length': 6, }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# If True, users can register
REGISTRATION_OPEN = True
# One-week activation window; you may, of course, use a different value.
ACCOUNT_ACTIVATION_DAYS = 7
# If True, the user will be automatically logged in.
REGISTRATION_AUTO_LOGIN = True
# The page you want users to arrive at after they successfully log in
LOGIN_REDIRECT_URL = '/'
# The page users are directed to if they are not logged in,
# and are trying to access pages requiring authentication
LOGIN_URL = '/login/'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/static/img/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/img')

TEMPLATE_CONTEXT_PROCESSORS = (
    #  other processors
    'django.core.context_processors.static',
    'django.template.context_processors.media',
)

SOUTH_MIGRATION_MODULES = {
    'data_importer': 'data_importer.south_migrations',
}

MIGRATION_MODULES = {
    'data_importer': 'data_importer.django_migrations'
},