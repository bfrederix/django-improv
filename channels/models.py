import datetime
import logging
import pytz

from django.db import models
from django.contrib.auth.models import User

from shows import service as shows_service
from utilities.fields import BoundedBigAutoField, FlexibleForeignKey

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VOTE_STYLE = [('options', 'Options'),
              ('player-options', 'Player Options'),
              ('repeatable-options', 'Repeatable Options'),
              ('repeatable-player-options', 'Repeatable Player Options'),
              ('vote-type-player-survivor', 'Vote Type Player Survivor'),
              ('show-player-survivor', 'Show Player Survivor'),
              ('vote-type-player-selected', 'Vote Type Selected Player Pool'),
              ('show-player-selected', 'Show Selected Player Pool'),
              ('all-players', 'All Players')]


class Channel(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=50, unique=True)
    display_name = models.CharField(blank=False, max_length=100)
    is_premium = models.BooleanField(blank=False, default=False)
    short_description = models.CharField(blank=True, null=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    thumbnail_url = models.CharField(blank=True, null=True, max_length=500)
    team_photo_url = models.CharField(blank=True, null=True, max_length=500)
    website = models.CharField(blank=True, null=True, max_length=500)
    facebook_page = models.CharField(blank=True, null=True, max_length=500)
    buy_tickets_link = models.CharField(blank=True, null=True, max_length=500)
    next_show = models.DateTimeField(blank=True, null=True)
    navbar_color = models.CharField(default="#4596FF", blank=False, max_length=20)
    background_color = models.CharField(default="#000000", blank=False, max_length=20)
    address = FlexibleForeignKey("ChannelAddress", blank=True, null=True)

    created = models.DateTimeField(blank=False)

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

    def get_next_interval(self, show_id=None, current_voted_not_required=False):
        current_voted = False
        # If given an interval
        if self.current_interval != None:
            # Loop through the intervals in order
            for i in range(0, len(self.interval_list())):
                if self.current_interval == self.interval_list()[i]:
                    # If a show was supplied, see if the interval was used
                    if show_id:
                        current_voted = shows_service.get_vote_type_interval_voted(show_id,
                                                                                   self.id,
                                                                                   self.current_interval)
                    #logger.info("current_voted: {0}".format(self.current_interval))
                    # If the current interval has already been voted on, or we don't require that
                    if current_voted or current_voted_not_required:
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

    def current_voted_player(self, show_id):
        # Only if we're displaying a result
        if self.result_seconds_remaining() > 0:
            # Get the current voted player if one exists
            return shows_service.get_current_voted_player(show_id,
                                                          self.id,
                                                          self.current_interval)
        return None

    def current_voted_suggestion(self, show_id):
        # Only if we're displaying a result
        if self.result_seconds_remaining() > 0:
            # Get the current voted player if one exists
            return shows_service.get_current_voted_suggestion(show_id,
                                                              self.id,
                                                              self.current_interval)
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

    def vote_type_used(self, show):
        return shows_service.get_vote_type_used(show, self)

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
                logger.info("interval_delta: {0}".format(interval_delta))
                # Determine when that interval ends
                interval_end = self.current_vote_init + datetime.timedelta(minutes=interval_delta)
            else:
                return 0
            if now >= interval_end:
                return 0
            else:
                return (interval_end - now).seconds
        return 0

    # Get the end of the current vote
    def vote_seconds_remaining(self):
        if self.current_vote_init:
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            vote_end = self.current_vote_init + datetime.timedelta(seconds=self.vote_length)
            if now >= vote_end:
                return 0
            else:
                return (vote_end - now).seconds
        return 0

    # Get the end of the current vote result
    def result_seconds_remaining(self):
        if self.current_vote_init:
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            vote_end = self.current_vote_init + datetime.timedelta(seconds=self.vote_length)
            result_end = self.current_vote_init + datetime.timedelta(seconds=self.vote_length + self.result_length)
            # if we're past the end of the result viewing
            if now >= result_end:
                return 0
            # If we're past the end of the vote
            elif now > vote_end:
                return (result_end - now).seconds
            # We haven't reached the result viewing
            else:
                return 0
        return 0

    def __unicode__(self):
        return self.name