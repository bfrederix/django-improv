class Medal(ndb.Model):
    name = ndb.StringProperty(required=True)
    display_name = ndb.StringProperty(required=True)
    description = ndb.TextProperty(required=True, indexed=False)
    image_filename = ndb.StringProperty(required=True)
    icon_filename = ndb.StringProperty(required=True)

    @property
    def img_path(self):
        return "/static/img/medals/%s" % self.image_filename

    @property
    def icon_path(self):
        return "/static/img/medals/%s" % self.icon_filename


class LeaderboardEntry(ndb.Model):
    show = ndb.KeyProperty(kind=Show, required=True)
    show_date = ndb.DateTimeProperty(required=True)
    user_id = ndb.StringProperty(required=True)
    points = ndb.IntegerProperty(default=0)
    wins = ndb.IntegerProperty(default=0)
    medals = ndb.KeyProperty(kind=Medal, repeated=True)

    @property
    def username(self):
        username = UserProfile.query(UserProfile.user_id == self.user_id).get().username
        try:
            return username.split('@')[0]
        except IndexError:
            return username

    @property
    def suggestions(self):
        return Suggestion.query(Suggestion.show == self.show,
                                Suggestion.user_id == self.user_id).count()


class LeaderboardSpan(ndb.Model):
    name = ndb.StringProperty(required=True)
    start_date = ndb.DateProperty()
    end_date = ndb.DateProperty()