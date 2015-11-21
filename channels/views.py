from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from channels.models import Channel, ChannelOwner, ChannelAdmin


def check_is_channel_admin(channel, user):
    # If the user isn't logged in
    if not getattr(user, 'id'):
        return False
    # Check if the user is a Channel Admin
    try:
        ChannelAdmin.objects.get(channel=channel,
                                 user=user)
    except ChannelAdmin.DoesNotExist:
        return False
    else:
        return True


class ChannelHomeView(View):
    template_name = 'channel_home.html'

    def get(self, request, *args, **kwargs):
        channel = get_object_or_404(Channel, name=kwargs.get('channel_name'))
        is_channel_admin = check_is_channel_admin(channel, request.user)
        return render(request,
                      self.template_name,
                      {'channel': channel,
                       'is_channel_admin': is_channel_admin})


class ChannelLeaderboardsView(View):
    template_name = 'channel_leaderboards.html'

    def get(self, request, *args, **kwargs):
        channel = get_object_or_404(Channel, name=kwargs.get('channel_name'))
        is_channel_admin = check_is_channel_admin(channel, request.user)

        return render(request,
                      self.template_name,
                      {'channel': channel,
                       'is_channel_admin': is_channel_admin})