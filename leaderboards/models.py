from django.db import models

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey


class Medal(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=100)
    display_name = models.CharField(blank=False, max_length=100)
    description = models.TextField(blank=False)
    image_filename = models.CharField(blank=False, max_length=255)
    icon_filename = models.CharField(blank=False, max_length=255)


class LeaderboardEntry(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("shows.Show", blank=False)
    show_date = models.DateTimeField(blank=False)
    user_id = models.BigIntegerField(blank=False)
    points = models.IntegerField(default=0, blank=True)
    wins = models.IntegerField(default=0, blank=True)

    # Add medals here based on leaderboard entry id
    # medals =


class LeaderboardEntryMedal(models.Model):
    medal = FlexibleForeignKey("Medal", blank=False)
    leaderboard_entry = FlexibleForeignKey("LeaderboardEntry", blank=False)


class LeaderboardSpan(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=100)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=False)