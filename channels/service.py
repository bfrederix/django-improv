import logging

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth.models import User

from channels.models import (ChannelAdmin, Channel, ChannelUser, ChannelOwner,
                             SuggestionPool, VoteType, VOTE_STYLE)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def channel_or_404(channel_key, channel_id=False):
    if channel_id:
        return get_object_or_404(Channel, id=channel_key)
    else:
        return get_object_or_404(Channel, name=channel_key)


def channel_from_request(request):
    channel = None
    # If the channel id was specified in the GET parameters
    if request.GET.get('channel_id'):
        # Try to fetch the channel by id
        try:
            channel = Channel.objects.get(pk=request.GET.get('channel_id'),
                                          archived=False)
            request.session['channel_id'] = channel.id
        except Channel.DoesNotExist:
            return None
    # Try and fetch it from the user's session
    elif request.session.get('channel_id'):
        # Try to fetch the channel by id
        try:
            channel = Channel.objects.get(pk=request.session.get('channel_id'),
                                          archived=False)
        except Channel.DoesNotExist:
            return None
    return channel


def fetch_channels():
    return Channel.objects.filter(archived=False).order_by('display_name')


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
    return VoteType.objects.filter(pk__in=vote_type_ids).order_by('-ordering')


def check_is_channel_admin(channel_name, user_id):
    # If the user isn't logged in or the channel doesn't exist
    if not user_id or not channel_name:
        return False
    channel = Channel.objects.get(name=channel_name)
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


def check_is_channel_owner(channel_name, user_id):
    channel = Channel.objects.get(name=channel_name)
    # If the user isn't logged in
    if not user_id:
        return False
    # Check if the user is a Channel Owner
    try:
        ChannelOwner.objects.get(channel=channel,
                                 user=user_id)
    except ChannelOwner.DoesNotExist:
        # Check to see if the user is a superuser
        user = User.objects.get(pk=user_id)
        if user.is_superuser:
            return True
        else:
            return False
    else:
        return True


def get_channels_by_admin(user_id):
    # If there isn't a user
    if not user_id:
        return []
    channels = []
    channel_admins = ChannelAdmin.objects.filter(user=user_id).exclude(channel__archived=True)
    for channel_admin in channel_admins:
        channels.append(channel_admin.channel)
    return channels


def get_channels_by_user(user_id):
    # If there isn't a user
    if not user_id:
        return []
    channels = []
    channel_users = ChannelUser.objects.filter(user=user_id).exclude(channel__archived=True)
    for channel_user in channel_users:
        channels.append(channel_user.channel)
    return channels

def get_channel_admins(channel_id):
    # If there isn't a channel
    if not channel_id:
        return []
    return ChannelAdmin.objects.filter(channel=channel_id)

def add_channel_admin(channel, user):
    admin, created = ChannelAdmin.objects.get_or_create(channel=channel,
                                                        user=user)
    return created


def remove_channel_admin(channel, user):
    try:
        ChannelAdmin.objects.get(channel=channel,
                                 user=user).delete()
    except ChannelAdmin.DoesNotExist:
        return


def add_channel_owner(channel, user):
    owner, created = ChannelOwner.objects.get_or_create(channel=channel,
                                                        user=user)
    return created


def remove_channel_owner(channel, user):
    try:
        ChannelOwner.objects.get(channel=channel,
                                 user=user).delete()
    except ChannelOwner.DoesNotExist:
        return


def channel_user_count(channel_id):
    return ChannelUser.objects.filter(channel=channel_id).count()


def update_channel_user(channel, user, leaderboard_entries):
    # If no user id was specified
    if not getattr(user, 'id'):
        # Do nothing
        return
    # Add the user as a ChannelUser
    channel_user, created = ChannelUser.objects.get_or_create(channel=channel,
                                                              user=user)
    cu_update = {'points': 0,
                 'suggestion_wins': 0,
                 'show_wins': 0}
    # Go through all the leaderboard entries for the user
    for le in leaderboard_entries:
        # Total points and suggestion wins
        cu_update['points'] += le.points
        cu_update['suggestion_wins'] += le.wins
        # If they won the show
        if le.show_win():
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


def start_next_interval(unused_intervals, vote_type):
    # Get the next interval
    next_interval = vote_type.get_next_interval(unused_intervals=unused_intervals)
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