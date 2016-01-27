from django.db import models
from django.contrib.auth.models import User

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey

from users import service as users_service


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
    show = FlexibleForeignKey("shows.Show", on_delete=models.CASCADE, blank=False)
    show_date = models.DateTimeField(blank=False)
    user = models.ForeignKey(User, blank=True, null=True)
    # Only used if user doesn't exist
    session_id = models.CharField(blank=True, null=True, max_length=255)
    points = models.IntegerField(default=0, blank=True, null=True)
    wins = models.IntegerField(default=0, blank=True, null=True)

    def __unicode__(self):
        return str(self.id)

    def user_id(self):
        if self.user:
            return self.user.id

    def username(self):
        user_profile = users_service.fetch_user_profile(self.user.id)
        return user_profile.safe_username()


class LeaderboardEntryMedal(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    medal = FlexibleForeignKey("Medal", blank=False)
    leaderboard_entry = FlexibleForeignKey("LeaderboardEntry", on_delete=models.CASCADE, blank=False)


class LeaderboardSpan(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    name = models.CharField(blank=False, max_length=100)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)

    created = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.name