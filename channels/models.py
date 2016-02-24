# DO NOT IMPORT SERVICES IN MODELS

import datetime
import logging
import pytz

from django.db import models
from django.contrib.auth.models import User

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VOTE_STYLE = [('options', 'Suggestion Options'),
              ('player-options', 'Player Suggestion Options'),
              ('repeatable-options', 'Repeatable Suggestion Options'),
              ('repeatable-player-options', 'Repeatable Player Suggestion Options'),
              ('vote-type-player-survivor', 'Vote Type Player Survivor'),
              ('show-player-survivor', 'Show Player Survivor'),
              ('vote-type-player-selected', 'Vote Type Selected Player Pool'),
              ('show-player-selected', 'Show Selected Player Pool'),
              ('all-players', 'All Players')]


class Channel(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=50, unique=True)
    display_name = models.CharField(blank=False, max_length=100)
    short_description = models.CharField(blank=True, null=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    thumbnail_url = models.CharField(blank=True, null=True, max_length=500)
    team_photo_url = models.CharField(blank=True, null=True, max_length=500)
    website = models.CharField(blank=True, null=True, max_length=500)
    facebook_page = models.CharField(blank=True, null=True, max_length=500)
    facebook_pixel = models.IntegerField(default=0, blank=True, null=True)
    buy_tickets_link = models.CharField(blank=True, null=True, max_length=500)
    next_show = models.DateTimeField(blank=True, null=True)
    navbar_color = models.CharField(default="#4596FF", blank=False, max_length=20)
    background_color = models.CharField(default="#000000", blank=False, max_length=20)
    address = FlexibleForeignKey("ChannelAddress", blank=True, null=True)
    is_premium = models.BooleanField(blank=False, default=False)
    premium_end_date = models.DateTimeField(blank=True, null=True)
    archived = models.BooleanField(blank=False, default=False)

    created = models.DateTimeField(blank=False)

    def future_next_show(self):
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        # Make sure the next show exists and is in the future
        if self.next_show and self.next_show > now:
            return self.next_show
        return None

    def __unicode__(self):
        return self.name


class ChannelAddress(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    street = models.CharField(blank=True, null=True, max_length=255)
    city = models.CharField(blank=True, null=True, max_length=100)
    state = models.CharField(blank=True, null=True, max_length=100)
    zipcode = models.CharField(blank=True, null=True, max_length=100)


class ChannelUser(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    user = models.ForeignKey(User)
    points = models.IntegerField(default=0, blank=True, null=True)
    suggestion_wins = models.IntegerField(default=0, blank=True, null=True)
    show_wins = models.IntegerField(default=0, blank=True, null=True)
    email_opt_in = models.BooleanField(blank=False, default=False)

class ChannelAdmin(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    user = models.ForeignKey(User)


class ChannelAdminInvite(models.Model):
    """Used to email hash to user and allow them to become admin of a channel"""
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    email = models.CharField(blank=False, max_length=100)
    hash_key = models.CharField(blank=False, max_length=100)


class ChannelOwner(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    user = models.ForeignKey(User)


class SuggestionPool(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("Channel", blank=False)
    name = models.CharField(blank=False, max_length=100)
    display_name = models.CharField(blank=False, max_length=100)
    description = models.TextField(blank=False)
    max_user_suggestions = models.IntegerField(default=5, blank=False)
    require_login = models.BooleanField(blank=False, default=False)
    active = models.BooleanField(default=True, blank=False)
    admin_only = models.BooleanField(default=True, blank=False)
    archived = models.BooleanField(blank=False, default=False)

    created = models.DateTimeField(blank=False)

    def __unicode__(self):
        return self.name


class VoteType(models.Model):
    # Defined at creation
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("Channel", blank=False)
    name = models.CharField(blank=False, max_length=100)
    display_name = models.CharField(blank=False, max_length=100)
    suggestion_pool = FlexibleForeignKey("SuggestionPool", null=True)
    intervals = models.CommaSeparatedIntegerField(blank=True, max_length=255)
    manual_interval_control = models.BooleanField(blank=False, default=True)
    style = models.CharField(choices=VOTE_STYLE, blank=False, max_length=100)
    preshow_selected = models.BooleanField(blank=False, default=False)
    ordering = models.IntegerField(default=0, blank=False)
    options = models.IntegerField(default=3, blank=False)
    vote_length = models.IntegerField(default=25, blank=False)
    result_length = models.IntegerField(default=10, blank=False)
    button_color = models.CharField(default="#003D7A", blank=False, max_length=100)
    require_login = models.BooleanField(blank=False, default=False)

    # Implicit Vote Type Options
    player_options = models.BooleanField(blank=False, default=False)
    players_only = models.BooleanField(blank=False, default=False)
    show_player_pool = models.BooleanField(blank=False, default=False)
    vote_type_player_pool = models.BooleanField(blank=False, default=False)
    eliminate_winning_player = models.BooleanField(blank=False, default=False)
    keep_suggestions = models.BooleanField(blank=False, default=False)
    # Vote Type is active or not
    active = models.BooleanField(default=True, blank=False)
    archived = models.BooleanField(blank=False, default=False)

    # Dynamic
    current_interval = models.IntegerField(default=None, blank=True, null=True)
    current_vote_init = models.DateTimeField(blank=True, null=True)

    created = models.DateTimeField(blank=False)

    def stripped_intervals(self):
        if self.intervals:
            return self.intervals.translate({ord(i):None for i in '[]L '})

    def interval_list(self):
        if self.intervals:
            return [int(i) for i in self.stripped_intervals().split(',')]
        else:
            return []

    def style_id(self):
        if self.style:
            count = 0
            for (name, display_name) in VOTE_STYLE:
                count += 1
                if self.style == name:
                    return count

    def vote_options_name(self):
        """ Either a suggestion pool display name or "Players"
        :return: str
        """
        if self.players_only:
            return "Players"
        elif self.suggestion_pool_id:
            return self.suggestion_pool.display_name
        return "Requires either Players or a Suggestion Pool"

    def get_next_interval(self, current_voted_not_required=False, unused_intervals=[]):
        current_voted = False
        # If given an interval
        if self.current_interval != None:
            # Loop through the intervals in order
            for i in range(0, len(self.interval_list())):
                # If the current interval matches an interval in the list
                if self.current_interval == self.interval_list()[i]:
                    # If we don't require a current voted interval
                    # OR if the current interval has already been voted on
                    if current_voted_not_required \
                        or not self.current_interval in unused_intervals:
                        # Get the next interval
                        try:
                            return int(self.interval_list()[i+1])
                        except IndexError:
                            return None
                    # Otherwise we should stay on the current interval
                    else:
                        return int(self.current_interval)
        # Otherwise, assume first interval
        else:
            try:
                return int(self.interval_list()[0])
            except IndexError:
                return None
        return None

    def remaining_intervals(self):
        # If a current interval exists, return the entire amount of intervals
        if self.current_interval == None:
            return len(self.interval_list())
        try:
            # Find the index of the current interval in the list
            interval_index = self.interval_list().index(self.current_interval)
        except ValueError:
            # Return no more intervals if the index isn't found
            return 0
        # Return the length of the list from the current interval to the end
        # Subtract one because where the index starts
        return len(self.interval_list()[interval_index:]) - 1

    # Get the end of the current interval
    def interval_seconds_remaining(self):
        # If an interval has occured
        if self.current_vote_init and self.current_interval != None:
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            next_interval = self.get_next_interval(current_voted_not_required=True)
            # If there is a next interval
            if next_interval:
                # Find the difference between this interval and the next
                interval_delta = next_interval - self.current_interval
                # Determine when that interval ends
                interval_end = self.current_vote_init + datetime.timedelta(minutes=interval_delta)
            else:
                return 0
            # If the we're past the end of the interval
            if now >= interval_end:
                return 0
            else:
                return (interval_end - now).seconds
        return 0

    # Get the end of the current vote
    def vote_seconds_remaining(self):
        # If this vote has been initialized, and this isn't a pre-show selected vote
        if self.current_vote_init and not self.preshow_selected:
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            vote_end = self.current_vote_init + datetime.timedelta(seconds=self.vote_length)
            if now > vote_end:
                return None
            else:
                return (vote_end - now).seconds
        return None

    # Get the end of the current vote result
    def result_seconds_remaining(self):
        if self.current_vote_init:
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            # If this isn't a pre-show selected vote
            if not self.preshow_selected:
                vote_end = self.current_vote_init + datetime.timedelta(seconds=self.vote_length)
                result_end = self.current_vote_init + datetime.timedelta(seconds=self.vote_length + self.result_length)
            # This is a pre-show selected vote
            else:
                # Set the vote end to current vote init (since we won't be voting
                vote_end = self.current_vote_init
                # Set the result end to the current vote init plus result length
                result_end = self.current_vote_init + datetime.timedelta(seconds=self.result_length)
            # if we're past the end of the result viewing
            if now > result_end:
                return None
            # If we're past the end of the vote
            elif now >= vote_end:
                return (result_end - now).seconds
            # We haven't reached the result viewing
            else:
                return None
        return None

    def __unicode__(self):
        return self.name