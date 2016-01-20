from django.db import models
from django.contrib.auth.models import User

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey


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
    sponsor_logo_url = models.CharField(blank=True, null=True, max_length=500)
    logo_url = models.CharField(blank=True, null=True, max_length=500)
    team_photo_url = models.CharField(blank=True, null=True, max_length=500)
    website = models.CharField(blank=True, null=True, max_length=500)
    facebook_page = models.CharField(blank=True, null=True, max_length=500)
    buy_tickets_link = models.CharField(blank=True, null=True, max_length=500)
    next_show = models.DateTimeField(blank=True, null=True)
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
    intervals = models.CommaSeparatedIntegerField(blank=True, max_length=100)
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
    current_interval = models.IntegerField(blank=True, null=True)
    current_vote_init = models.DateTimeField(blank=True, null=True)

    created = models.DateTimeField(blank=False)

    def stripped_intervals(self):
        if self.intervals:
            return self.intervals.translate({ord(i):None for i in '[]L '})

    def style_id(self):
        if self.style:
            count = 0
            for (name, display_name) in VOTE_STYLE:
                count += 1
                if self.style == name:
                    return count

    def __unicode__(self):
        return self.name