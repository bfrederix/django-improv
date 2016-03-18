from django.conf import settings
from users import service as users_service
from channels import service as channels_service

def default_context(request):
    # Get the channel from the request path
    channel = channels_service.channel_from_request(request)
    # If the channel exists, set the name and display name of the channel
    if channel:
        channel_name = channel.name
        channel_display_name = channel.display_name
    # Otherwise set the name and display name of the channel to None
    else:
        channel_name = None
        channel_display_name = None
    return {'DEBUG': settings.DEBUG,
            'CSS_URL': settings.CSS_PATH,
            'HOME_THEME_URL': settings.HOME_THEME_PATH,
            'JS_URL': settings.JS_PATH,
            'IMAGE_URL': settings.IMAGE_PATH,
            'AUDIO_URL': settings.AUDIO_PATH,
            'PLAYERS_URL': settings.PLAYERS_PATH,
            'FACEBOOK_ID': settings.SOCIAL_AUTH_FACEBOOK_KEY,
            'user_profile': users_service.fetch_user_profile(getattr(request.user, 'id')),
            'channel_name': channel_name,
            'channel_display_name': channel_display_name}