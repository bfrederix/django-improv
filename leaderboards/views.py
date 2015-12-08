from django.shortcuts import render
from django.views.generic import View

from leaderboards import LEADERBOARD_MAX_PER_PAGE
from channels.service import (channel_or_404, check_is_channel_admin,
                              channel_user_count)
from shows.service import show_or_404


class ChannelLeaderboardsView(View):
    template_name = 'leaderboards/channel_leaderboards.html'

    def get(self, request, *args, **kwargs):

        channel_name = kwargs.get('channel_name')
        channel = channel_or_404(channel_name)
        show_id = kwargs.get('show_id')
        page = request.GET.get('page', 1)
        max_pages = int(channel_user_count(channel.id)/LEADERBOARD_MAX_PER_PAGE)
        if show_id:
            show = show_or_404(show_id)
        else:
            show = None
        is_channel_admin = check_is_channel_admin(channel, getattr(request.user, 'id'))

        return render(request,
                      self.template_name,
                      {'channel': channel,
                       'show': show,
                       'page': page,
                       'max_per_page': LEADERBOARD_MAX_PER_PAGE,
                       'max_pages': max_pages,
                       'is_channel_admin': is_channel_admin})