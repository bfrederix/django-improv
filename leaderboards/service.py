import datetime
import logging
import pytz

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from leaderboards.models import (LeaderboardEntry, LeaderboardEntryMedal,
                                 LeaderboardSpan, Medal)
from utilities.helper_functions import multikeysort

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_leaderboard_entries_by_user(user_id):
    # if a user was specified
    if user_id:
        return LeaderboardEntry.objects.filter(user=user_id)
    # Return an empty list
    else:
        return []


def leaderboard_span_or_404(pk):
    return get_object_or_404(LeaderboardSpan, pk=pk)


def create_leaderboard_span(name, channel, start_date, end_date):
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    # Get or create the leaderboard span
    leaderboard_span, created = LeaderboardSpan.objects.get_or_create(
                                    name=name,
                                    channel=channel,
                                    start_date=start_date,
                                    end_date=end_date,
                                    created=now)
    return leaderboard_span


def fetch_leaderboard_entries_by_show(show_id, leaderboard_order=False):
    leaderboard_entries = LeaderboardEntry.objects.filter(show=show_id).exclude(user=None)
    if leaderboard_order:
        return leaderboard_entries.order_by('-wins', '-points')
    return leaderboard_entries


def fetch_medals():
    return Medal.objects.all()


def fetch_medal_ids_by_leaderboard_entry(leaderboard_entry_id):
    return LeaderboardEntryMedal.objects.filter(leaderboard_entry=leaderboard_entry_id).values_list('medal_id', flat=True)


def get_span_user_count(channel_id, start_time, end_time):
    return LeaderboardEntry.objects.filter(
               channel=channel_id,
               show_date__gte=start_time,
               show_date__lte=end_time
           ).exclude(user=None).values('user').distinct().count()


def aggregate_leaderboard_entries_by_user(leaderboard_entries):
    user_list = []
    user_dict = {}
    for entry in leaderboard_entries:
        # Set defaults for everything
        user_dict.setdefault(entry.user_id, {})
        user_dict[entry.user_id].setdefault('points', 0)
        user_dict[entry.user_id].setdefault('show_wins', 0)
        user_dict[entry.user_id].setdefault('suggestion_wins', 0)

        # Add the wins, points, medals, and suggestions for the user from this particular show
        user_dict[entry.user_id]['points'] += entry.points
        user_dict[entry.user_id]['show_wins'] += int(entry.show_win())
        user_dict[entry.user_id]['suggestion_wins'] += entry.wins
    # Turn that dictionary into a list of dictionaries
    for user_id, value_dict in user_dict.items():
        user_data = {'user_id': user_id}
        user_data.update(value_dict)
        user_list.append(user_data)
    # Sort the list by suggestion wins
    return multikeysort(user_list, ['-suggestion_wins', '-points'])


def award_leaderboard_medals(leaderboard_entries, user_suggestion_count):
    # If there are entries
    if leaderboard_entries:
        # Get the winning sorted entry
        winning_entry = leaderboard_entries[0]
    else:
        winning_entry = None

    medal_dict = {'points-without-win': {'max': 0, 'leaderboard_entry': None},
                  'win-percentage': {'max': 0, 'leaderboard_entry': None}}
    for entry in leaderboard_entries:
        # Determine if a user has reached a new high for points without a win
        if not entry.wins and entry.points > medal_dict['points-without-win']['max']:
            medal_dict['points-without-win']['max'] = entry.points
            medal_dict['points-without-win']['leaderboard_entry'] = entry

        try:
            win_percentage = int(100 * (float(entry.wins) / float(user_suggestion_count[entry.user_id])))
        except ZeroDivisionError:
            win_percentage = 0
        # Determine if a user has reached a new high for points with wins factored in
        if win_percentage > medal_dict['win-percentage']['max']:
            medal_dict['win-percentage']['max'] = win_percentage
            medal_dict['win-percentage']['leaderboard_entry'] = entry

    # Award the winner medal if a winner exists
    if winning_entry:
        winner_medal = Medal.objects.get(name='winner')
        LeaderboardEntryMedal.objects.get_or_create(
            medal=winner_medal,
            leaderboard_entry=winning_entry)
    # Award the points without a win (Poo) medal if exists
    if medal_dict['points-without-win']['leaderboard_entry']:
        points_without_win_medal = Medal.objects.get(name='points-without-win')
        LeaderboardEntryMedal.objects.get_or_create(
            medal=points_without_win_medal,
            leaderboard_entry=medal_dict['points-without-win']['leaderboard_entry'])

    # Award the win percentage medal if exists
    if medal_dict['win-percentage']['leaderboard_entry']:
        win_percentage_medal = Medal.objects.get(name='win-percentage')
        LeaderboardEntryMedal.objects.get_or_create(
                medal=win_percentage_medal,
                leaderboard_entry=medal_dict['win-percentage']['leaderboard_entry'])


def get_or_create_leaderboard_entry(channel, show, user, session_id):
    leaderboard_entry_kwargs = {'channel': channel,
                                'show': show}
    # If there is a user
    if user:
        leaderboard_entry_kwargs['user'] = user
    # If they have a session
    elif session_id:
        leaderboard_entry_kwargs['session_id'] = session_id
    try:
        return LeaderboardEntry.objects.get(**leaderboard_entry_kwargs)
    except ObjectDoesNotExist:
        leaderboard_entry_kwargs['show_date'] = show.created
        leaderboard_entry = LeaderboardEntry(**leaderboard_entry_kwargs)
        leaderboard_entry.save()
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
        leaderboard_entry.save()


def add_leaderboard_entry_points(channel, show, user, suggestion_user, suggestion_session_id, require_login):
    le_kwargs = {'channel': channel,
                 'show': show,
                 'show_date': show.created}
    # If the user is logged in
    if user:
        # If everyone is logged in
        if require_login:
            points = 1
        # Because this particular user is logged in
        else:
            points = 2
    else:
        points = 1
    # If there is a suggestion user
    if suggestion_user:
        le_kwargs['user'] = suggestion_user
    # Otherwise just one point
    else:
        le_kwargs['session_id'] = suggestion_session_id
    # Get the leaderboard entry
    leaderboard_entry = LeaderboardEntry.objects.get(**le_kwargs)
    # Add the points to the entry
    leaderboard_entry.points += points
    leaderboard_entry.save()


def add_leaderboard_entry_win(show_id, user_id, session_id):
    le_kwargs = {'show': show_id}
    # If the user is logged in
    if user_id:
        le_kwargs['user'] = user_id
    # Otherwise just one point
    else:
        le_kwargs['session_id'] = session_id
    try:
        # Get or create the leaderboard entry
        leaderboard_entry = LeaderboardEntry.objects.get(**le_kwargs)
        # Add the win to the entry
        leaderboard_entry.wins += 1
        leaderboard_entry.save()
    except ObjectDoesNotExist:
        return