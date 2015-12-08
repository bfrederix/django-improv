from django.db import models
from django.contrib.auth.models import User

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey


class Channel(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=50, unique=True)
    display_name = models.CharField(blank=False, max_length=100)
    is_premium = models.BooleanField(blank=False, default=False)
    short_description = models.CharField(blank=True, max_length=100)
    description = models.TextField(blank=True)
    thumbnail_url = models.CharField(blank=True, max_length=500)
    sponsor_logo_url = models.CharField(blank=True, max_length=500)
    logo_url = models.CharField(blank=True, max_length=500)
    team_photo_url = models.CharField(blank=True, max_length=500)
    website = models.CharField(blank=True, max_length=500)
    facebook_page = models.CharField(blank=True, max_length=500)
    address = FlexibleForeignKey("ChannelAddress", blank=True, null=True)
    buy_tickets_link = models.CharField(blank=True, max_length=500)
    next_show = models.DateTimeField(blank=True)

    def __unicode__(self):
        return self.name


class ChannelAddress(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    street = models.CharField(blank=True, max_length=255)
    city = models.CharField(blank=True, max_length=100)
    state = models.CharField(blank=True, max_length=100)
    zipcode = models.CharField(blank=True, max_length=100)


class ChannelUser(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    user = models.ForeignKey(User)
    points = models.IntegerField(default=0, blank=True, null=True)
    suggestion_wins = models.IntegerField(default=0, blank=True, null=True)
    show_wins = models.IntegerField(default=0, blank=True, null=True)

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