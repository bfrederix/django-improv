import logging

from django.shortcuts import get_object_or_404
from django.http import Http404

from channels.models import (ChannelAdmin, Channel, ChannelUser,
                             SuggestionPool, VoteType, VOTE_STYLE)
from leaderboards import service as leaderboards_service

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
        logger.info("Blah")
        raise Http404
    try:
        return VOTE_STYLE[vote_style_id-1]
    except IndexError:
        logger.info('Could not find vote style: {0}, {1}'.format(vote_style_id,
                                                                 VOTE_STYLE))
        raise Http404


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


def update_channel_user(channel_id, user_id):
    user_id = int(user_id)
    channel_user, created = ChannelUser.objects.get_or_create(channel=channel_id, user=user_id)
    les = leaderboards_service.fetch_leaderboard_entries_by_user(user_id)
    cu_update = {'points': 0,
                 'suggestion_wins': 0,
                 'show_wins': 0}
    # Go through all the leaderboard entries for the user
    for le in les:
        cu_update['points'] += le.points
        cu_update['suggestion_wins'] += le.wins
        show_entries = leaderboards_service.fetch_leaderboard_entries_by_show(le.show.id,
                                                                              leaderboard_order=True)
        if show_entries[0].user.id == user_id:
            cu_update['show_wins'] += 1
    for key, value in cu_update.items():
        setattr(channel_user, key, value)
    channel_user.save()


def fetch_channel_users(channel_id, leaderboard_sort=False):
    channel_users = ChannelUser.objects.filter(channel=channel_id)
    if leaderboard_sort:
        channel_users = channel_users.order_by('-suggestion_wins', '-points')
    return channel_users