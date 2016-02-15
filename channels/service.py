import datetime
import logging
import pytz

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth.models import User

from channels.models import (ChannelAdmin, Channel, ChannelUser,
                             SuggestionPool, VoteType, VOTE_STYLE)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def channel_or_404(channel_key, channel_id=False):
    if channel_id:
        return get_object_or_404(Channel, id=channel_key)
    else:
        return get_object_or_404(Channel, name=channel_key)


def suggestion_pool_or_404(suggestion_pool_id):
    return get_object_or_404(SuggestionPool, id=suggestion_pool_id)


def vote_type_or_404(vote_type_id):
    return get_object_or_404(VoteType, id=vote_type_id)


def vote_style_or_404(vote_style_id):
    if not vote_style_id:
        raise Http404
    try:
        return VOTE_STYLE[vote_style_id-1]
    except IndexError:
        logger.info('Could not find vote style: {0}, {1}'.format(vote_style_id,
                                                                 VOTE_STYLE))
        raise Http404


def fetch_vote_types_by_ids(vote_type_ids):
    return VoteType.objects.filter(pk__in=vote_type_ids)


def check_is_channel_admin(channel_name, user_id):
    channel = Channel.objects.get(name=channel_name)
    # If the user isn't logged in
    if not user_id:
        return False
    # Check if the user is a Channel Admin
    try:
        ChannelAdmin.objects.get(channel=channel,
                                 user=user_id)
    except ChannelAdmin.DoesNotExist:
        # Check to see if the user is a superuser
        user = User.objects.get(pk=user_id)
        if user.is_superuser:
            return True
        else:
            return False
    else:
        return True


def get_channels_by_admin(user_id):
    channels = []
    channel_admins = ChannelAdmin.objects.filter(user=user_id)
    for channel_admin in channel_admins:
        channels.append(channel_admin.channel)
    return channels


def channel_user_count(channel_id):
    return ChannelUser.objects.filter(channel=channel_id).count()


def update_channel_user(channel_id, user_id, leaderboard_entries):
    user_id = int(user_id)
    # Add the user as a ChannelUser
    channel_user, created = ChannelUser.objects.get_or_create(channel=channel_id, user=user_id)
    cu_update = {'points': 0,
                 'suggestion_wins': 0,
                 'show_wins': 0}
    # Go through all the leaderboard entries for the user
    for le in leaderboard_entries:
        # Total points and suggestion wins
        cu_update['points'] += le.points
        cu_update['suggestion_wins'] += le.wins
        # If they won the show
        if le.show_win:
            cu_update['show_wins'] += 1
    # Set the overall leaderboard data on the Channel User
    for key, value in cu_update.items():
        setattr(channel_user, key, value)
    channel_user.save()


def fetch_channel_users(channel_id, leaderboard_sort=False):
    channel_users = ChannelUser.objects.filter(channel=channel_id)
    if leaderboard_sort:
        channel_users = channel_users.order_by('-suggestion_wins', '-points')
    return channel_users


def vote_type_style_to_fields(style):
    fields = {'player_options': False,
              'players_only': False,
              'show_player_pool': False,
              'vote_type_player_pool': False,
              'eliminate_winning_player': False,
              'keep_suggestions': False}
    if style == 'options':
        pass
    elif style == 'player-options':
        fields['player_options'] = True
    elif style == 'repeatable-options':
        fields['keep_suggestions'] = True
    elif style == 'repeatable-player-options':
        fields['player_options'] = True
        fields['keep_suggestions'] = True
    elif style == 'vote-type-player-survivor':
        fields['players_only'] = True
        fields['vote_type_player_pool'] = True
    elif style == 'show-player-survivor':
        fields['players_only'] = True
        fields['show_player_pool'] = True
    elif style == 'vote-type-player-selected':
        fields['players_only'] = True
        fields['vote_type_player_pool'] = True
        fields['eliminate_winning_player'] = True
    elif style == 'show-player-selected':
        fields['players_only'] = True
        fields['show_player_pool'] = True
        fields['eliminate_winning_player'] = True
    elif style == 'all-players':
        fields['players_only'] = True
    return fields


def vote_type_available_options(vote_type,
                                show_players_count=0,
                                show_vote_type_player_pool_count=0,
                                show_player_pool_count=0):
    # If it's player options
    if vote_type.players_only:
        # If it uses a pool for the show
        if vote_type.show_player_pool:
            return show_player_pool_count
        elif vote_type.vote_type_player_pool:
            pass
        else:
            pass
    # If it's a suggestion pool option
    else:
        pass


def start_next_interval(show_id, vote_type):
    # Get the next interval
    next_interval = vote_type.get_next_interval(show_id=show_id)
    # If there is a next interval
    if next_interval != None:
        # Set the current interval to the next interval
        vote_type.current_interval = next_interval
        vote_type.save()
    return next_interval


def get_current_vote_state(vote_type_ids):
    """
    Determine what the current vote state is based on the vote types available
    :param vote_type_ids: list
    :return: {'display': 'default/voting/result',
              'vote_type_id': vote_type_id}
    """
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    # Loop through all the available vote types
    for vote_type in VoteType.objects.filter(pk__in=vote_type_ids).order_by('-current_vote_init'):
        vote_remaining = vote_type.vote_seconds_remaining()
        result_remaining = vote_type.result_seconds_remaining()
        # If there are seconds still remaining on the result display
        if result_remaining != None and result_remaining >= 0:
            return {'display': 'result',
                    'vote_type_id': vote_type.id}
        # If there are seconds still remaining on the voting display
        elif vote_remaining != None and vote_remaining >= 0:
            return {'display': 'voting',
                    'vote_type_id': vote_type.id}
    # Otherwise show the default screen
    return {'display': 'default'}