from django.shortcuts import get_object_or_404

from channels.models import ChannelAdmin, Channel, ChannelUser


def channel_or_404(channel_name):
    return get_object_or_404(Channel, name=channel_name)


def check_is_channel_admin(channel_name, user_id):
    channel = Channel.objects.get(name=channel_name)
    # If the user isn't logged in
    if not user_id:
        return False
    # Check if the user is a Channel Admin
    try:
        ChannelAdmin.objects.get(channel=channel,
                                 user=user_id)
    except ChannelAdmin.DoesNotExist:
        return False
    else:
        return True

def channel_user_count(channel_id):
    return ChannelUser.objects.filter(channel=channel_id).count()