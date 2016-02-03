from conf.settings import *

DEBUG = False

TEMPLATE_DEBUG = False

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