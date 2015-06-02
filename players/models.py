class Player(ndb.Model):
    name = ndb.StringProperty(required=True)
    photo_filename = ndb.StringProperty(required=True, indexed=False)
    star = ndb.BooleanProperty(default=False)
    date_added = ndb.DateTimeProperty()

'''
    @property
    def img_path(self):
        return "/static/img/players/%s" % self.photo_filename
'''