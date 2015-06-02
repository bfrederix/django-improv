class UserProfile(ndb.Model):
    user_id = ndb.StringProperty(required=True)
    username = ndb.StringProperty(default=None)
    strip_username = ndb.StringProperty(default=None)
    email = ndb.StringProperty(default=None)
    login_type = ndb.StringProperty(default=None)
    current_session = ndb.StringProperty(default=None)
    fb_access_token = ndb.StringProperty(default=None)
    created = ndb.DateTimeProperty(required=True)

    def put(self, *args, **kwargs):
        if self.username:
            self.strip_username = self.username.replace(" ", "").lower()
        return super(UserProfile, self).put(*args, **kwargs)

    @property
    def username_email_strip(self):
        try:
            return self.username.split('@')[0]
        except IndexError:
            return self.username


class EmailOptOut(ndb.Model):
    email = ndb.StringProperty(required=True)