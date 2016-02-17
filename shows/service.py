import re
import random
import datetime
import logging
import pytz

from django.shortcuts import get_object_or_404
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from shows.models import (Show, Suggestion, VotedItem,
                          VoteOption, LiveVote,
                          ShowVoteType, ShowPlayer,
                          ShowVoteTypePlayerPool, ShowInterval)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def show_or_404(show_id):
    return get_object_or_404(Show, pk=show_id)

def get_current_show(channel_id):
    now_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    # Set the longest back we would consider a show still running
    longest_showtime_ago = now_utc - datetime.timedelta(hours=48)
    # Fetch all shows that started within the last 48 hours
    shows = Show.objects.filter(channel=channel_id,
                                created__gt=longest_showtime_ago).order_by('-created')
    # If there were shows in the last 48 hours
    if shows:
        # Return the most recent show, as long as it hasn't ended already
        if shows[0].show_end() > now_utc:
            return shows[0]
    return None


def get_show_interval(show_id, vote_type_id, interval):
    try:
        return ShowInterval.objects.get(show=show_id,
                                        vote_type=vote_type_id,
                                        interval=interval)
    except ObjectDoesNotExist:
        return None


def fetch_suggestions(user_id=None, show_id=None, suggestion_pool_id=None,
                      used=None, count=False):
    kwargs = {}
    if user_id:
        kwargs['user'] = user_id
    if show_id:
        kwargs['show'] = show_id
    if suggestion_pool_id:
        kwargs['suggestion_pool'] = suggestion_pool_id
    if used != None:
        kwargs['used'] = used
    queryset = Suggestion.objects.filter(**kwargs)

    if count:
        return queryset.count()
    else:
        return queryset


def suggestion_or_404(suggestion_id):
    return get_object_or_404(Suggestion, pk=suggestion_id)


def fetch_randomized_suggestions(show_id, suggestion_pool_id, option_count):
    # Make sure there is a proper option count
    if not option_count:
        raise ValueError("Option count needs to be higher than 0")
    # Return un-used suggestion keys, sorted by vote, and only if they've appeared less than twice
    unused_suggestions = Suggestion.objects.filter(
                             show=show_id,
                             suggestion_pool=suggestion_pool_id,
                             used=False,
                             amount_voted_on__lt=2).order_by('amount_voted_on',
                                                             '-preshow_value',
                                                             'created')[:option_count*2]
    # If there are less than the option amount left that haven't been voted on twice
    # Allow suggestions that have been voted on twice already
    if len(unused_suggestions) < option_count:
        # Fetch un-used suggestion keys
        unused_suggestions = Suggestion.objects.filter(
                                 show=show_id,
                                 suggestion_pool=suggestion_pool_id,
                                 used=False).order_by('-preshow_value',
                                                      'created')[:option_count*2]
    # Get a randomized sample of the top "options" amount of suggestion
    random_sample = list(random.sample(
                            set(unused_suggestions),
                            min(option_count, len(unused_suggestions))))
    return random_sample[:option_count]


def update_suggestions_session_to_user(show_id, session_id, user_id):
    # Make sure we have a show, session_id, and user
    if not show_id or not session_id or not user_id:
        return
    # Try to fetch the suggestions by show and session id
    try:
        suggestions = Suggestion.objects.filter(show=show_id,
                                                session_id=session_id)
    # No suggestions with that session id
    except:
        return
    # Update the suggestions with the user
    else:
        # Get the user by id
        user = User.objects.get(pk=user_id)
        for suggestion in suggestions:
            # Update the user
            suggestion.user = user
            # Remove the session id
            suggestion.session_id = None
            suggestion.save()


def fetch_voted_items_by_show(show_id, ordered=False):
    voted_items = VotedItem.objects.filter(show=show_id)
    if ordered:
        voted_items = voted_items.order_by('vote_type__ordering', 'interval')
    return voted_items


def fetch_vote_options(show_id=None, vote_type_id=None, interval=None):
    kwargs = {}
    if show_id:
       kwargs['show'] = show_id
    if vote_type_id:
       kwargs['vote_type'] = vote_type_id
    if interval is not None:
       kwargs['interval'] = interval
    return VoteOption.objects.filter(**kwargs).order_by('option_number')


def fetch_vote_option_ids(show_id=None, vote_type_id=None, interval=None):
    return fetch_vote_options(show_id=show_id,
                              vote_type_id=vote_type_id,
                              interval=interval).values_list('id', flat=True)

def get_option_live_votes(vote_option_id):
    return LiveVote.objects.filter(vote_option=vote_option_id).count()


def get_winning_option(vote_options):
    max_count = None
    most_voted_option = None

    # Loop through all the options
    for vote_option in vote_options:
        # Get the count of live votes for this option
        vote_count = get_option_live_votes(vote_option.id)
        # If the vote count is the biggest we've seen so far
        if max_count == None or vote_count > max_count:
            # Capture the most voted option and its count
            most_voted_option = vote_option
            max_count = vote_count
    return most_voted_option


def get_option(vote_option_id):
    return VoteOption.objects.get(pk=vote_option_id)


def fetch_option(show_id, vote_type_id, interval, option_number):
    # Get the vote option
    try:
        return VoteOption.objects.get(show=show_id,
                                      vote_type=vote_type_id,
                                      interval=interval,
                                      option_number=option_number)
    except ObjectDoesNotExist:
        return None


def live_votes_exist(show_interval, user_id, session_id):
    live_vote_kwargs = {'show_interval': show_interval}
    # If a user exists
    if user_id:
        # Only look up the live vote by user
        live_vote_kwargs['user'] = user_id
    # Otherwise use the session id
    else:
        live_vote_kwargs['session_id'] = session_id
    try:
        return bool(LiveVote.objects.filter(**live_vote_kwargs).count())
    except Exception as e:
        logger.info(str(e))


def create_live_votes(vote_option, show_interval, user, session_id, require_login):
    # Create a live vote
    LiveVote(vote_option=vote_option,
             show_interval=show_interval,
             user=user,
             session_id=session_id).save()
    # If the user is logged in, but not everyone is logged in
    if user and not require_login:
        # Create another live vote
        LiveVote(vote_option=vote_option,
                 show_interval=show_interval,
                 user=user,
                 session_id=session_id).save()


def get_show_vote_type_player_pool_ids(vote_type_id, show_id, count=False, used=None):
    """
    Get the players remaining for the vote type in the show
    :param vote_type_id: int/str
    :param show_id: int/str
    :param count: bool: Only return the count
    :param used: bool: Decide whether to return used or not used
    :return: List of Player objects
    """
    svtpp_kwargs = {'show': show_id,
                    'vote_type': vote_type_id}
    if used != None:
        svtpp_kwargs['used'] = used
    queryset = ShowVoteTypePlayerPool.objects.filter(**svtpp_kwargs)
    # If we only want the count
    if count:
        return queryset.count()
    # Return the remaining players
    else:
        return [svtpp_p for svtpp_p in queryset.values_list('player_id', flat=True)]


def get_vote_types_suggestion_pools(vote_types):
    suggestion_pools = []
    for vote_type in vote_types:
        # If the vote type has a suggestion pool and it isn't already in the list
        if vote_type.suggestion_pool_id \
            and not vote_type.suggestion_pool in suggestion_pools:
            # Add it to the list of suggestion pools for the show
            suggestion_pools.append(vote_type.suggestion_pool)
    return suggestion_pools


def get_current_voted(show_id, vote_type_id, interval):
    try:
        voted_item = VotedItem.objects.get(show=show_id,
                                           vote_type=vote_type_id,
                                           interval=interval)
    except ObjectDoesNotExist:
        return None
    else:
        return voted_item


def get_vote_type_interval_used(show_id, vote_type_id, interval):
    return bool(get_current_voted(show_id, vote_type_id, interval))


def set_show_interval_random_player(show, vote_type, interval):
    try:
        # Randomly select a player from the show
        player = ShowPlayer.objects.filter(show=show).order_by('?')[0].player
    except IndexError:
        raise IndexError("You must have players to use this vote style.")
    # Get or create the show interval
    show_interval, created = ShowInterval.objects.get_or_create(show=show,
                                                                vote_type=vote_type,
                                                                interval=interval)
    # Set the player and save the show interval
    show_interval.player = player
    show_interval.save()


def set_voting_options(show, vote_type, interval,
                       suggestions=[]):
    vote_option_kwargs = {
        'show': show,
        'vote_type': vote_type,
        'interval': interval,
        'suggestion': None,
        'player': None}
    # If we are doing a repeatable vote type
    if vote_type.keep_suggestions:
        # Get all the vote options of this vote type and delete them
        vote_options = VoteOption.objects.filter(show=show,
                                                 vote_type=vote_type,
                                                 interval=interval)
        # NOTE: This will delete live votes too
        vote_options.delete()
    # If there are suggestions
    if suggestions:
        vote_option_kwargs['option_number'] = 1
        # Mark the suggestions as voted on
        for suggestion in suggestions:
            suggestion.voted_on = True
            suggestion.amount_voted_on += 1
            suggestion.save()
            # If there is a player attached to the suggestion
            if vote_type.player_options:
                # If this vote type has intervals
                if vote_type.intervals:
                    # Fetch the player from the Show Interval
                    vote_option_kwargs['player'] = ShowInterval.objects.get(
                                                       show=vote_option_kwargs['show'],
                                                       vote_type=vote_option_kwargs['vote_type'],
                                                       interval=vote_option_kwargs['interval']).player
            vote_option_kwargs['suggestion'] = suggestion
            # Create the suggestion vote options
            VoteOption.objects.get_or_create(**vote_option_kwargs)
            # Set the option number of the option
            vote_option_kwargs['option_number'] += 1
    else:
        # Set just the unused players from the show as options
        if vote_type.show_player_pool:
            show_players = ShowPlayer.objects.filter(show=show,
                                                     used=False)
        # Set just the usused players from this vote type as options
        elif vote_type.vote_type_player_pool:
            show_players = ShowVoteTypePlayerPool.objects.filter(show=show,
                                                                 vote_type=vote_type,
                                                                 used=False)
        # All Show Players as vote options
        else:
            show_players = ShowPlayer.objects.filter(show=show)
        vote_option_kwargs['option_number'] = 1
        # Set the players as vote options
        for show_player in show_players:
            vote_option_kwargs['player'] = show_player.player
            # Create the suggestion vote options
            VoteOption.objects.get_or_create(**vote_option_kwargs)
            # Set the option number of the option
            vote_option_kwargs['option_number'] += 1


def set_voted_option(show, vote_type, interval, vote_option):
    voted_option_kwargs = {
        'show': show,
        'vote_type': vote_type,
        'interval': interval,
        'vote_option': vote_option}
    # If there was a suggestion
    if vote_option.suggestion:
        # If we aren't keeping voted on suggestions
        if not vote_type.keep_suggestions:
            vote_option.suggestion.used = True
            vote_option.suggestion.save()
    # If it was a player only vote
    if vote_option.player:
        # If the player was from the show player pool
        if vote_type.show_player_pool:
            # Fetch the show player and mark them as used
            show_player = ShowPlayer.objects.get(show=show,
                                                 player=vote_option.player)
            show_player.used = True
            show_player.save()
        # If the player was from the vote type player pool
        elif vote_type.vote_type_player_pool:
            # Fetch the vote type player and mark them as used
            vote_type_player = ShowVoteTypePlayerPool.objects.get(show=show,
                                                                  vote_type=vote_type,
                                                                  player=vote_option.player)
            vote_type_player.used = True
            vote_type_player.save()
    # Create the voted item
    VotedItem.objects.get_or_create(**voted_option_kwargs)


def suggestions_maxed(show, suggestion_pool, user_id=None, session_id=None):
    # If a user id was given
    if user_id:
        # Get the number of suggestions made by the user id
        suggestion_count = Suggestion.objects.filter(show=show,
                                                     suggestion_pool=suggestion_pool,
                                                     user=user_id).count()
    elif session_id:
        # Get the number of suggestions made by the session
        suggestion_count = Suggestion.objects.filter(show=show,
                                                     suggestion_pool=suggestion_pool,
                                                     session_id=session_id).count()
    else:
        return False

    # Return True if the suggestion count is greater than or equal to the max
    if suggestion_count >= suggestion_pool.max_user_suggestions:
        return True
    else:
        return False


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


def create_show(channel, vote_types, show_length, players=[],
                star_players=[], combined_players=[],
                embedded_youtube=None, photo_link=None):
    if vote_types:
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