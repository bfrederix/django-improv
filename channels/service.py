from django.shortcuts import get_object_or_404

from channels.models import ChannelAdmin, Channel, ChannelUser
from leaderboards import service as leaderboards_service

def channel_or_404(channel_key, channel_id=False):
    if channel_id:
        return get_object_or_404(Channel, id=channel_key)
    else:
        return get_object_or_404(Channel, name=channel_key)


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