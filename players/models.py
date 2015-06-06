from django.db import models


class Player(models.Model):
    name = models.CharField(blank=False)
    photo_filename = models.CharField(blank=False)
    star = models.BooleanField(default=False, blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=False)