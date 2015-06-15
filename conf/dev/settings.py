from conf.settings import *

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'voteprov_prod',
        'USER': 'voteprovprod',
        'PASSWORD': 'pr0dpr0v',
        'HOST': 'voteprov.crtjwt7ubwk0.us-west-2.rds.amazonaws.com',
        'OPTIONS': {
            'options': '-c search_path=public'
        }
    }
}