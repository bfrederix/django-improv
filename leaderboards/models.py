from django.db import models


class Medal(models.Model):
    name = models.CharField(blank=False)
    display_name = models.CharField(blank=False)
    description = models.TextField(blank=False)
    image_filename = models.CharField(blank=False)
    icon_filename = models.CharField(blank=False)


class LeaderboardEntry(models.Model):
    show = models.ForeignKey("Show", blank=False)
    show_date = models.DateTimeField(blank=False)
    user_id = models.BigIntegerField(blank=False)
    points = models.IntegerField(default=0, blank=True)
    wins = models.IntegerField(default=0, blank=True)
    medals = models.ManyToManyField("Medal", blank=True)


class LeaderboardSpan(models.Model):
    name = models.CharField(blank=False)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=False)