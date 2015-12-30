from django.db import models
from django.contrib.auth.models import User

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey


VOTE_STYLE = [('player-options', 'Player Options'),
              ('player-pool', 'Player Pool'),
              ('options', 'Options'),
              ('preshow-voted', 'Pre-show Voted'),
              ('all-players', 'All Players'),
              ('test', 'Test')]


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
    timezone = models.CharField(blank=True, null=True, max_length=100)
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
    preshow_voted = models.BooleanField(blank=False, default=False)
    intervals = models.CommaSeparatedIntegerField(blank=True, max_length=100)
    manual_interval_control = models.BooleanField(blank=False, default=True)
    style = models.CharField(choices=VOTE_STYLE, blank=False, max_length=100)
    ordering = models.IntegerField(default=0, blank=False)
    options = models.IntegerField(default=3, blank=False)
    vote_length = models.IntegerField(default=25, blank=False)
    result_length = models.IntegerField(default=10, blank=False)
    randomize_amount = models.IntegerField(default=6, blank=False)
    button_color = models.CharField(default="#003D7A", blank=False, max_length=100)
    active = models.BooleanField(default=True, blank=False)

    # Dynamic
    current_interval = models.IntegerField(blank=True, null=True)
    current_init = models.DateTimeField(blank=True)

    created = models.DateTimeField(blank=False)

    def __unicode__(self):
        return self.name