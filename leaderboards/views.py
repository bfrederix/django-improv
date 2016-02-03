from django.shortcuts import render
from django.views.generic import View

from leaderboards import LEADERBOARD_MAX_PER_PAGE
from leaderboards.models import LeaderboardEntry, LeaderboardEntryMedal
from channels.service import (channel_or_404, check_is_channel_admin,
                              channel_user_count)
from shows.service import show_or_404
from utilities import views as view_utils


class ChannelLeaderboardsView(view_utils.ShowView):
    template_name = 'leaderboards/channel_leaderboards.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        show_id = kwargs.get('show_id')
        page = request.GET.get('page', 1)
        max_pages = int(channel_user_count(context['channel'].id)/LEADERBOARD_MAX_PER_PAGE)
        if show_id:
            show = show_or_404(show_id)
            les = LeaderboardEntry.objects.filter(show=show)
            medals_awarded = bool(LeaderboardEntryMedal.objects.filter(leaderboard_entry__in=les))
        else:
            show = None
            medals_awarded = False
        context.update({'show': show,
                        'medals_awarded': medals_awarded,
                        'page': page,
                        'max_per_page': LEADERBOARD_MAX_PER_PAGE,
                        'max_pages': max_pages})

        return render(request,
                      self.template_name,
                      context)