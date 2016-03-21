from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    # Their django user
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Id pulled from the social platform they created their account with
    social_id = models.CharField(blank=True, null=True, max_length=100)
    username = models.CharField(blank=False, max_length=100, unique=True)
    first_name = models.CharField(blank=True, null=True, max_length=100)
    last_name = models.CharField(blank=True, null=True, max_length=100)
    strip_username = models.CharField(default=None, blank=False, max_length=100, unique=True)
    email = models.CharField(default=None, blank=True, max_length=100)
    login_type = models.CharField(default=None, blank=False, max_length=50)
    site_email_opt_in = models.BooleanField(blank=False, default=False)

    created = models.DateTimeField(blank=False)

    def __unicode__(self):
        return self.strip_username

    def save(self, *args, **kwargs):
        self.strip_username = self.username.replace(" ", "").lower()
        super(UserProfile, self).save(*args, **kwargs)

    def safe_username(self):
        try:
            return self.username.split('@')[0]
        except IndexError:
            return self.username
