from django.db import models

from utilities.fields import BoundedBigAutoField


class Player(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=100)
    photo_filename = models.CharField(blank=False, max_length=255)
    star = models.BooleanField(default=False, blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=False)