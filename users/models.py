from django.db import models


class UserProfile(models.Model):
    user_id = models.CharField(primary_key=True, blank=False, max_length=100, unique=True)
    is_admin = models.BooleanField(blank=False, default=False)
    username = models.CharField(blank=False, max_length=100, unique=True)
    strip_username = models.CharField(default=None, blank=False, max_length=100)
    email = models.CharField(default=None, blank=True, max_length=100)
    login_type = models.CharField(default=None, blank=False, max_length=50)
    current_session = models.CharField(default=None, blank=True, max_length=255,
                                       null=True)
    fb_access_token = models.CharField(default=None, blank=True, max_length=255,
                                       null=True)
    email_opt_in = models.BooleanField(blank=False, default=False)

    created = models.DateTimeField(auto_now_add=True, blank=False)

    def __unicode__(self):
        return self.strip_username

'''
    def put(self, *args, **kwargs):
        if self.username:
            self.strip_username = self.username.replace(" ", "").lower()
        return super(UserProfile, self).put(*args, **kwargs)

class EmailOptOut(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    email = models.CharField(blank=False, max_length=100)

    created = models.DateTimeField(auto_now_add=True, blank=False)

    def __unicode__(self):
        return self.email
'''