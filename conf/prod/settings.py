from conf.settings import *

DEBUG = False

TEMPLATE_DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = [
    '.dumpedit.com', # Allow domain and subdomains
    '.dumpedit.com.', # Also allow FQDN and subdomains
]

STATIC_ROOT = "/var/www/static/"

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

# Facebook OAuth2 DEV settings
# http://stackoverflow.com/a/29132451
SOCIAL_AUTH_FACEBOOK_KEY = '***REMOVED***'
SOCIAL_AUTH_FACEBOOK_SECRET = '***REMOVED***'

# Google OAuth2 settings
# http://stackoverflow.com/a/20732762/264567
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '***REMOVED***'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '***REMOVED***'

STRIPE_PUBLIC_KEY = "***REMOVED***"
STRIPE_SECRET_KEY = "***REMOVED***"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}