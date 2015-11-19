from django.db import models

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey


class UserProfile(models.Model):
    # Their django user id
    user_id = models.BigIntegerField(primary_key=True, blank=False, null=False, unique=True)
    # Id pulled from the social service they created their account with
    social_id = models.CharField(blank=True, null=True, max_length=100)
    username = models.CharField(blank=False, max_length=100, unique=True)
    first_name = models.CharField(blank=True, null=True, max_length=100)
    last_name = models.CharField(blank=True, null=True, max_length=100)
    strip_username = models.CharField(default=None, blank=False, max_length=100)
    email = models.CharField(default=None, blank=True, max_length=100)
    login_type = models.CharField(default=None, blank=False, max_length=50)
    improvote_email_opt_in = models.BooleanField(blank=False, default=False)
    channels_email_opt_in = models.BooleanField(blank=False, default=False)

    created = models.DateTimeField(auto_now_add=True, blank=False)

    def __unicode__(self):
        return self.strip_username

    def save(self, *args, **kwargs):
        self.strip_username = self.username.replace(" ", "").lower()
        super(UserProfile, self).save(*args, **kwargs)


class UserChannelEmailOptIn(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    # Django user id
    user_id = models.BigIntegerField(blank=False, unique=True)
    opt_in = models.BooleanField(blank=False, default=False)
