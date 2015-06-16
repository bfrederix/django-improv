from django.db import models

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey


class ShowRecap(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("shows.Show", blank=False)
    winners_photo_url = models.CharField(blank=True, null=True, max_length=255)
    highlights_video = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return str(self.show)