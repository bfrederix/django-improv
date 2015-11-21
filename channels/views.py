from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from channels.models import Channel
from channels.service import check_is_channel_admin, channel_or_404


class ChannelHomeView(View):
    template_name = 'channel_home.html'

    def get(self, request, *args, **kwargs):
        channel_name = kwargs.get('channel_name')
        channel = channel_or_404(channel_name)
        is_channel_admin = check_is_channel_admin(channel, getattr(request.user, 'id'))
        return render(request,
                      self.template_name,
                      {'channel': channel,
                       'is_channel_admin': is_channel_admin})
