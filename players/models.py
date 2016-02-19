from django.db import models

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey


class Player(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    name = models.CharField(blank=False, max_length=100)
    photo_url = models.CharField(blank=False, max_length=500)
    star = models.BooleanField(default=False, blank=True)
    active = models.BooleanField(default=True, blank=False)
    archived = models.BooleanField(blank=False, default=False)

    created = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.name