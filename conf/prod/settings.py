from conf.settings import *

DEBUG = False

TEMPLATE_DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django',
        'USER': 'django',
        'PASSWORD': '***REMOVED***',
        # voteprov-postgres droplet (prod postgres server)
        'HOST': '104.236.161.125',
        'PORT': '5432',
    }
}

STRIPE_PUBLIC_KEY = "***REMOVED***"
STRIPE_SECRET_KEY = "***REMOVED***"