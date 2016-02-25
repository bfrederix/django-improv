import datetime
import pytz

from django.db import models
from django.contrib.auth.models import User

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey


class Forum(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=50, unique=True)
    display_name = models.CharField(blank=False, max_length=100)
    description = models.CharField(blank=True, null=True, max_length=100)

    def __unicode__(self):
        return self.display_name

    def last_post(self):
        try:
            return Reply.objects.filter(forum=self.id).order_by('-created')[0].created
        except IndexError:
            return None

    def thread_count(self):
        return Thread.objects.filter(forum=self.id).count()

class Thread(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    forum = FlexibleForeignKey("Forum", blank=False, on_delete=models.CASCADE)
    subject = models.CharField(blank=False, null=False, max_length=100)
    message = models.TextField(blank=False, null=False)
    sticky = models.BooleanField(blank=False, default=False)

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(blank=False)
    updated = models.DateTimeField(blank=False)

    def __unicode__(self):
        return self.subject

    def replies_count(self):
        return Reply.objects.filter(thread=self.id).count()

    def last_post(self):
        replies = Reply.objects.filter(thread=self.id).order_by('-created')
        if replies:
            return replies[0]
        else:
            return self

class Reply(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    forum = FlexibleForeignKey("Forum", blank=False, on_delete=models.CASCADE)
    thread = FlexibleForeignKey("Thread", blank=False, on_delete=models.CASCADE)
    message = models.TextField(blank=False, null=False)

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(blank=False)

    def __unicode__(self):
        return self.message

    def save(self, *args, **kwargs):
        super(Reply, self).save(*args, **kwargs)
        self.thread.updated = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        self.thread.save()