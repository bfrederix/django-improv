# NEVER CALL THIS FROM A SERVICE OR MODEL, ONLY FROM VIEWS/API VIEWS/URLS

import datetime
import logging
import pytz

from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from channels import service as channels_service
from shows import service as shows_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ShowView(View):

    def get_default_channel_context(self, request, *args, **kwargs):
        context = {'channel': self.channel,
                   'is_channel_admin': self.is_channel_admin,
                   'current_show': self.current_show}
        # Get the channels that the user is an admin of
        context['admin_channels'] = channels_service.get_channels_by_admin(
                                            getattr(self.request.user, 'id'))
        # If they aren't an admin of any channels
        if not context['admin_channels']:
            # Get the channels that the user is part of
            context['user_channels'] = channels_service.get_channels_by_user(
                                            getattr(self.request.user, 'id'))
        if self.current_show:
            # Get the vote types by a list of ids
            vote_types = channels_service.fetch_vote_types_by_ids(
                                                self.current_show.vote_types())
            # Get the suggestion pools for the current show if it exists
            context['suggestion_pools'] = shows_service.get_vote_types_suggestion_pools(
                                                vote_types)
        return context

    def dispatch(self, request, *args, **kwargs):
        # Get the channel ids from the kwargs
        channel_name = kwargs.get('channel_name')
        channel_id = kwargs.get('channel_id')
        # If a channel name was given
        if channel_name:
            self.channel = channels_service.channel_or_404(channel_name)
        # If a channel id was given
        elif channel_id:
            self.channel = channels_service.channel_or_404(channel_id,
                                                           channel_id=True)
        else:
            self.channel = None
        # If a channel was found
        if self.channel:
            # If the channel has been "deleted"
            if self.channel.archived:
                return redirect("dumpedit_home")
            # See if the user is an admin
            self.is_channel_admin = channels_service.check_is_channel_admin(self.channel,
                                                                            getattr(self.request.user, 'id'))
            # Determine if there is a current show for this channel
            self.current_show = shows_service.get_current_show(self.channel.id)
        else:
            self.is_channel_admin = False
            self.current_show = None
        # If the current show is locked and the user isn't an admin
        if self.current_show and getattr(self.current_show, 'locked') \
            and not self.is_channel_admin:
            url_kwargs = {'channel_name': self.channel.name,
                          'show_id': self.current_show.id}
            # Get the live vote path
            live_vote_path = reverse('show_live_vote', kwargs=url_kwargs)
            # Get the vote receiver path
            vote_receiver_path = reverse('show_vote_receiver', kwargs=url_kwargs)
            # If the user isn't voting, redirect them to voting
            if not request.path in [live_vote_path, vote_receiver_path]:
                return redirect(live_vote_path)
        return super(ShowView, self).dispatch(request, *args, **kwargs)


def start_new_interval(show, vote_type):
    """
    Start the next interval for the show of the given vote type
    :return: None
    """
    # Get the unused intervals for this vote type
    unused_intervals = shows_service.get_unused_interval_list(show.id, vote_type)
    logger.info(unused_intervals)
    # Set the vote type's next interval start
    next_interval = channels_service.start_next_interval(unused_intervals, vote_type)
    # Set the start of the vote type's current interval to now
    vote_type.current_vote_init = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    vote_type.save()
    # if it's a players only vote type
    if vote_type.players_only:
        suggestions = []
    # Otherwise, fetch a randomized (yet sorted) amount of suggestions
    else:
        suggestions = shows_service.fetch_randomized_suggestions(show.id,
                                                                 vote_type.suggestion_pool_id,
                                                                 vote_type.options)
    # Set the voting options
    # NOTE: Live Votes get deleted for repeateable
    shows_service.set_voting_options(show,
                                     vote_type,
                                     next_interval,
                                     suggestions=suggestions)
    # If this isn't an interval vote and the vote type has player options
    if not vote_type.intervals and vote_type.player_options:
        # Set a random player for the vote options
        shows_service.set_show_interval_random_player(show,
                                                      vote_type,
                                                      vote_type.current_interval)
    # Make sure the show is locked
    show.locked = True
    # Set the show's current vote type
    show.current_vote_type = vote_type
    show.save()


def robots_txt(request):
    robots_txt = """User-agent: *
Disallow: /"""

    live_txt = """User-agent: *
Allow: /$
Allow: /leaderboards
Allow: /recap
Allow: /user
Allow: /medals
Disallow: /"""
    return HttpResponse(robots_txt, content_type='text/plain')

def loader_io(request):
    robots_txt = "loaderio-9b6fa50492da1609dc61b9198b767688"
    return HttpResponse(robots_txt, content_type='text/plain')