import datetime

from django.shortcuts import render
from django.http import HttpResponseNotFound

from leaderboards import LEADERBOARD_MAX_PER_PAGE
from leaderboards.models import LeaderboardEntry, LeaderboardEntryMedal
from channels.service import (channel_user_count)
from shows.service import show_or_404
from leaderboards import service as leaderboards_service
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

class ChannelLeaderboardSpansView(view_utils.ShowView):
    template_name = 'leaderboards/channel_leaderboards.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        start = kwargs.get('start')
        end = kwargs.get('end')
        # Convert the start and end to datetimes
        start_time = datetime.datetime.strptime(start, "%Y%m%d")
        end_time = datetime.datetime.strptime(end, "%Y%m%d")
        page = request.GET.get('page', 1)
        span_user_count = leaderboards_service.get_span_user_count(context['channel'].id,
                                                                   start_time,
                                                                   end_time)
        max_pages = int(span_user_count/LEADERBOARD_MAX_PER_PAGE)
        # Make sure we have a start and end to the span
        if not start or not end:
            return HttpResponseNotFound('Invalid Span Dates.')
        context.update({'start': start,
                        'end': end,
                        'page': page,
                        'max_per_page': LEADERBOARD_MAX_PER_PAGE,
                        'max_pages': max_pages})

        return render(request,
                      self.template_name,
                      context)