import re
import random

from django.shortcuts import get_object_or_404

from shows.models import (Show, Suggestion, VotedItem,
                          VoteOptions, OptionSuggestion)


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


def create_show(channel_id, players, vote_types):
    if player_list and vote_type_list:
        players = []
        star_players = []
        # Get the players for the show
        for player in player_list:
            player_key = get_player(key_id=player, key_only=True)
            # If they're a star player, add them to the star list
            if player_key.get().star:
                star_players.append(player_key)
            else:
                players.append(player_key)
        combined_players = players + star_players
        show = create_show({'players': combined_players,
                            'player_pool': combined_players}).get()
        # Get and sort the vote types by ordering
        vts = [get_vote_type(key_id=x) for x in vote_type_list]
        vote_types = sorted(vts, key=lambda x: x.ordering)
        # Add the vote types to the show
        for vote_type in vote_types:
            # Reset the vote type's current interval
            vote_type.current_interval = None
            vote_type.put()
            # Add the vote type to the show
            show.vote_types.append(vote_type.key)
            # Get the maximum voting options from the vote type
            # And store it if it's greater than the show's current vote options
            show.vote_options = max(show.vote_options, vote_type.options)
            # If the vote type has intervals
            if vote_type.has_intervals:
                # If this suggestion vote has players attached
                if vote_type.interval_uses_players:
                    # Make a copy of the list of players and randomize it
                    rand_players = get_rand_player_list(players, star_players=star_players)
                    # Add the intervals to the show
                    for interval in vote_type.intervals:
                        # If random players list gets empty, refill it with more players
                        if len(rand_players) == 0:
                            rand_players = get_rand_player_list(players, star_players=star_players)
                        # Pop a random player off the list and create a ShowInterval
                        create_show_interval({'show': show.key,
                                              'player': rand_players.pop(),
                                              'interval': interval,
                                              'vote_type': vote_type.key})
                else:
                    # Add the suggestion intervals to the show
                    for interval in vote_type.intervals:
                        # Create a ShowInterval
                        create_show_interval({'show': show.key,
                                              'interval': interval,
                                              'vote_type': vote_type.key})


def validate_youtube(url):
    youtube_regex = (r'(https?://)?(www\.)?' '(youtube|youtu|youtube-nocookie)\.(com|be)/' '(watch\?.*?(?=v=)v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)

    return youtube_regex_match