from django.db import models

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey


class Channel(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=50)
    display_name = models.CharField(blank=False, max_length=100)
    short_description = models.CharField(blank=True, max_length=100)
    description = models.TextField(blank=True)
    thumbnail_url = models.CharField(blank=True, max_length=500)
    logo_url = models.CharField(blank=True, max_length=500)
    team_photo_url = models.CharField(blank=True, max_length=500)
    website = models.CharField(blank=True, max_length=500)
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
