from django.conf import settings

def default_context(request):
    return {'DEBUG': settings.DEBUG,
            'CSS_URL': settings.CSS_PATH,
            'HOME_THEME_URL': settings.HOME_THEME_PATH,
            'JS_URL': settings.JS_PATH,
            'IMAGE_URL': settings.IMAGE_PATH,
            'AUDIO_URL': settings.AUDIO_PATH,
            'PLAYERS_URL': settings.PLAYERS_PATH,
            'FACEBOOK_ID': settings.SOCIAL_AUTH_FACEBOOK_KEY}