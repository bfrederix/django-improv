import logging

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from leaderboards.models import LeaderboardEntry, LeaderboardEntryMedal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_leaderboard_entries_by_user(user_id):
    return LeaderboardEntry.objects.filter(user=user_id)


def fetch_leaderboard_entries_by_show(show_id, leaderboard_order=False):
    leaderboard_entries = LeaderboardEntry.objects.filter(show=show_id)
    if leaderboard_order:
        return leaderboard_entries.order_by('-wins', '-points')
    return leaderboard_entries


def fetch_medal_ids_by_leaderboard_entry(leaderboard_entry_id):
    return LeaderboardEntryMedal.objects.filter(leaderboard_entry=leaderboard_entry_id).values_list('medal_id', flat=True)


def get_or_create_leaderboard_entry(channel, show, user, session_id):
    leaderboard_entry, created = LeaderboardEntry.objects.get_or_create(channel=channel,
                                                                        show=show,
                                                                        show_date=show.created,
                                                                        user=user,
                                                                        session_id=session_id)
    return leaderboard_entry


def update_leaderboard_entry_session_to_user(show_id, session_id, user_id):
    """
    If a leaderboard entry exists with a session id attached to it, and we
    have a user, make sure the leaderboard entry is attached to the user
    instead of the session id.

    ALSO NOTE: This implicitly updates the ChannelUser leaderboard data

    :param show_id:
    :param session_id:
    :param user_id:
    :return: None
    """

    # Make sure we have a show, session_id, and user
    if not show_id or not session_id or not user_id:
        return
    # Try to get the leaderboard entry by show and session id
    try:
        leaderboard_entry = LeaderboardEntry.objects.get(show=show_id,
                                                         session_id=session_id)
    # No leaderboard entry with that session id
    except ObjectDoesNotExist:
        return
    # Update the leaderboard entry with the user
    else:
        # Get the user by id
        user = User.objects.get(pk=user_id)
        # Update the user
        leaderboard_entry.user = user
        # Remove the session id
        leaderboard_entry.session_id = None
        # This will update the ChannelUser leaderboard data implicitly
        leaderboard_entry.save()


def add_leaderboard_entry_points(channel, show, user, session_id, require_login):
    le_kwargs = {'channel': channel,
                 'show': show,
                 'show_date': show.created}
    # If the user is logged in
    if user:
        le_kwargs['user'] = user
        # If everyone is logged in
        if require_login:
            points = 1
        # Because this particular user is logged in
        else:
            points = 2
    # Otherwise just one point
    else:
        le_kwargs['session_id'] = session_id
        points = 1
    # Get or create the leaderboard entry
    leaderboard_entry = LeaderboardEntry.objects.get(**le_kwargs)
    # Add the points to the entry
    leaderboard_entry.points += points
    # NOTE: ChannelUser data gets updated as part of the LeaderboardEntry save method
    leaderboard_entry.save()