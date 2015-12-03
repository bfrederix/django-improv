from django.shortcuts import render
from django.views.generic import View

from channels.service import channel_or_404, check_is_channel_admin
from shows.service import show_or_404


class ChannelLeaderboardsView(View):
    template_name = 'leaderboards/channel_leaderboards.html'

    def get(self, request, *args, **kwargs):
        channel_name = kwargs.get('channel_name')
        channel = channel_or_404(channel_name)
        show_id = kwargs.get('show_id')
        if show_id:
            show = show_or_404(show_id)
        else:
            show = None
        is_channel_admin = check_is_channel_admin(channel, getattr(request.user, 'id'))

        return render(request,
                      self.template_name,
                      {'channel': channel,
                       'show': show,
                       'is_channel_admin': is_channel_admin})