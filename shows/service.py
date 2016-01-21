import re
import random
import datetime
import logging
import pytz

from django.shortcuts import get_object_or_404
from django.db.models import Max

from shows.models import (Show, Suggestion, VotedItem,
                          VoteOptions, OptionSuggestion,
                          ShowVoteType, ShowPlayer,
                          ShowVoteTypePlayerPool, ShowInterval)
from players import service as players_service
from channels import service as channels_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def show_or_404(show_id):
    return get_object_or_404(Show, pk=show_id)


def fetch_suggestion_count_by_user(user_id, show_id=None):
    if user_id:
        kwargs = {'user': user_id}
        if show_id:
            kwargs['show'] = show_id
        return Suggestion.objects.filter(**kwargs).count()
    else:
        return 0


def suggestion_or_404(suggestion_id):
    return get_object_or_404(Suggestion, pk=suggestion_id)


def fetch_voted_items_by_show(show_id, ordered=False):
    voted_items = VotedItem.objects.filter(show=show_id)
    if ordered:
        voted_items = voted_items.order_by('vote_type__ordering', 'interval')
    return voted_items


def fetch_vote_options(show=None, vote_type=None, interval=None):
    kwargs = {}
    if show:
       kwargs['show'] = show
    if vote_type:
       kwargs['vote_type'] = vote_type
    if interval is not None:
       kwargs['interval'] = interval
    return VoteOptions.objects.filter(**kwargs)


def fetch_option_suggestion(vote_option_id):
    return OptionSuggestion.objects.filter(vote_option=vote_option_id)


def get_rand_player_list(players, star_players=[]):
    """Create a random list of players,
       putting star players at the front of the list for popping
    """
    # Make a copy of the list of players and randomize it
    rand_players = list(players)
    random.shuffle(rand_players, random.random)
    if star_players:
        for star in star_players:
            rand_players.append(star)
    return rand_players


def create_show(channel, vote_type_ids, show_length, player_ids=None,
                embedded_youtube=None, photo_link=None):
    if vote_type_ids:
        players = []
        star_players = []
        combined_players = []
        # If there are players selected for the show
        if player_ids:
            # Get the regular players
            players = players_service.fetch_players_by_ids(player_ids, star=False)
            # Get the star players
            star_players = players_service.fetch_players_by_ids(player_ids, star=True)
            # Get both star and regular players
            combined_players = players_service.fetch_players_by_ids(player_ids)
        # Get the vote types selected
        vote_types = channels_service.fetch_vote_types_by_ids(vote_type_ids)
        # Get the max voting options (ignoring players only vote types)
        voting_options = vote_types.exclude(players_only=True).aggregate(Max('options')).values()[0]
        # If there are any vote types that are "player only"
        if [vt.players_only for vt in vote_types]:
            voting_options = max(voting_options, len(combined_players))
        show = Show(channel=channel,
                    show_length=show_length,
                    vote_options=voting_options,
                    created=datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
                    locked=False,
                    embedded_youtube=embedded_youtube,
                    photo_link=photo_link)
        show.save()
        # If there are players for the show, add them to the show
        if combined_players:
            for player in combined_players:
                ShowPlayer.objects.get_or_create(show=show,
                                                 player=player,
                                                 used=False)
        # Add the vote types to the show
        for vote_type in vote_types:
            # Reset the vote type's current interval
            vote_type.current_interval = None
            vote_type.save()
            # Create the show vote type
            ShowVoteType.objects.get_or_create(show=show,
                                               vote_type=vote_type)
            # If there are players for the vote type, add them to the vote type
            if vote_type.vote_type_player_pool and combined_players:
                for player in combined_players:
                    ShowVoteTypePlayerPool.objects.get_or_create(show=show,
                                                                 player=player,
                                                                 vote_type=vote_type,
                                                                 used=False)
            # If the vote type has intervals
            if vote_type.intervals:
                logger.info("Show: {0} Intervals: {1}".format(show.id, vote_type.intervals))
                # If this suggestion vote has players attached
                if vote_type.player_options:
                    # Make a copy of the list of players and randomize it
                    rand_players = get_rand_player_list(players, star_players=star_players)
                    # Add the intervals to the show
                    for interval in vote_type.intervals.split(','):
                        # If random players list gets empty, refill it with more players
                        if len(rand_players) == 0:
                            rand_players = get_rand_player_list(players, star_players=star_players)
                        logger.info("Random Players: {0}".format(rand_players))
                        # Pop a random player off the list and create a ShowInterval
                        ShowInterval.objects.get_or_create(show=show,
                                                           player=rand_players.pop(),
                                                           interval=int(interval),
                                                           vote_type=vote_type)
                else:
                    # Add the suggestion intervals to the show
                    for interval in vote_type.intervals.split(','):
                        # Create a ShowInterval
                        ShowInterval.objects.get_or_create(show=show,
                                                           interval=int(interval),
                                                           vote_type=vote_type)
    else:
        raise ValueError("Vote Types are required for a show.")

    return show


def validate_youtube(url):
    youtube_regex = (r'(https?://)?(www\.)?' '(youtube|youtu|youtube-nocookie)\.(com|be)/' '(watch\?.*?(?=v=)v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)

    return youtube_regex_match