from conf.settings import *

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django',
        'USER': 'django',
        'PASSWORD': '***REMOVED***',
        # voteprov-django droplet (prod django server, but dev db)
        'HOST': '***REMOVED***',
        'PORT': '5432',
    }
}

# Facebook OAuth2 DEV settings
# http://stackoverflow.com/a/29132451
SOCIAL_AUTH_FACEBOOK_KEY = '***REMOVED***'
SOCIAL_AUTH_FACEBOOK_SECRET = '***REMOVED***'

# Google OAuth2 settings
# http://stackoverflow.com/a/20732762/264567
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '118682384942-2hhu73gl3tj84kb9gcaonilsu4hpbl3e.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'LvDuyEZbK_B9n1SdqL8QyBKg'