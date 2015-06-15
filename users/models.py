from django.db import models

from utilities.fields import BoundedBigAutoField


class UserProfile(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    is_admin = models.BooleanField(blank=False, default=False)
    user_id = models.CharField(blank=False, max_length=100, unique=True)
    username = models.CharField(default=None, blank=False, max_length=100)
    strip_username = models.CharField(default=None, blank=False, max_length=100)
    email = models.CharField(default=None, blank=True, max_length=100)
    login_type = models.CharField(default=None, blank=False, max_length=50)
    current_session = models.CharField(default=None, blank=True, max_length=255,
                                       null=True)
    fb_access_token = models.CharField(default=None, blank=True, max_length=255,
                                       null=True)

    created = models.DateTimeField(auto_now_add=True, blank=False)

'''
    def put(self, *args, **kwargs):
        if self.username:
            self.strip_username = self.username.replace(" ", "").lower()
        return super(UserProfile, self).put(*args, **kwargs)
'''


class EmailOptOut(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    email = models.CharField(blank=False, max_length=100)

    created = models.DateTimeField(auto_now_add=True, blank=False)