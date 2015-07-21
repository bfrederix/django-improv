from conf.settings import *

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django',
        'USER': 'django',
        'PASSWORD': '***REMOVED***',
        'HOST': '***REMOVED***',
        'PORT': '5432',
    }
}