from django.db import models

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey


class Medal(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=100)
    display_name = models.CharField(blank=False, max_length=100)
    description = models.TextField(blank=False)
    image_filename = models.CharField(blank=False, max_length=255)
    icon_filename = models.CharField(blank=False, max_length=255)

    def __unicode__(self):
        return self.name

class LeaderboardEntry(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    show = FlexibleForeignKey("shows.Show", blank=False)
    show_date = models.DateTimeField(blank=False)
    user_id = models.CharField(blank=False, max_length=100)
    points = models.IntegerField(default=0, blank=True, null=True)
    wins = models.IntegerField(default=0, blank=True, null=True)

    def __unicode__(self):
        return str(self.id)

class LeaderboardEntryMedal(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    medal = FlexibleForeignKey("Medal", blank=False)
    leaderboard_entry = FlexibleForeignKey("LeaderboardEntry", blank=False)


class LeaderboardSpan(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    name = models.CharField(blank=False, max_length=100)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return self.name