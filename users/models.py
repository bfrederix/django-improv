from django.db import models


class UserProfile(models.Model):
    user_id = models.BigIntegerField(blank=False)
    username = models.CharField(default=None, blank=False)
    strip_username = models.CharField(default=None, blank=False)
    email = models.CharField(default=None, blank=True)
    login_type = models.CharField(default=None, blank=False)
    current_session = models.CharField(default=None, blank=True)
    fb_access_token = models.CharField(default=None, blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=False)

'''
    def put(self, *args, **kwargs):
        if self.username:
            self.strip_username = self.username.replace(" ", "").lower()
        return super(UserProfile, self).put(*args, **kwargs)
'''


class EmailOptOut(models.Model):
    email = models.CharField(blank=False)

    created = models.DateTimeField(auto_now_add=True, blank=False)