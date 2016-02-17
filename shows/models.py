import datetime

from django.db import models
from django.contrib.auth.models import User

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey

DATE_FORMAT_STR = "%a. %b. %d, %Y @%I%p"


class Show(models.Model):
    # Assigned to show on creation
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    # Show length in minutes
    show_length = models.IntegerField(blank=False, default=180)
    # Show vote options (Max of vote type and players)
    vote_options = models.IntegerField(blank=False, default=3)

    created = models.DateTimeField(blank=False)
    first_vote_start = models.DateTimeField(blank=True, null=True)

    # Changes during live show
    current_vote_type = FlexibleForeignKey("channels.VoteType", blank=True, related_name='+',
                                           null=True)
    current_vote_init = models.DateTimeField(blank=True, null=True)
    locked = models.BooleanField(default=False, blank=False)

    # For Recap
    photo_link = models.CharField(blank=True, null=True, max_length=500)
    embedded_youtube = models.CharField(blank=True, null=True, max_length=500)

    def __unicode__(self):
        return self.created.strftime(DATE_FORMAT_STR)

    def show_end(self):
        return self.created + datetime.timedelta(minutes=self.show_length)

    def formatted_date(self):
        return self.created.strftime(DATE_FORMAT_STR)

    def formatted_youtube(self):
        if self.embedded_youtube:
            return "https://www.youtube.com/embed/{0}".format(self.embedded_youtube)
        return ''

    # All vote types by show id
    def vote_types(self):
        return [svt_vt_id for svt_vt_id in ShowVoteType.objects.filter(show=self.id).values_list('vote_type_id', flat=True)\
                                                                                    .order_by("vote_type__ordering")]

    # All players by show id
    def players(self):
        return [sp_p_id for sp_p_id in ShowPlayer.objects.filter(show=self.id).values_list('player_id', flat=True)]

    # The remaining un-used players in the show player pool
    def remaining_show_players(self):
        return [sp_p_id for sp_p_id in ShowPlayer.objects.filter(show=self.id).exclude(used=True)\
                                                                                   .values_list('player_id', flat=True)]

    def show_seconds_remaining(self):
        if self.created and self.show_length:
            # Get the show end
            show_end = self.created + datetime.timedelta(minutes=self.show_length)
            return (show_end - self.created).seconds

# Doing this as a Many to Many so I can use BigInts
class ShowVoteType(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    vote_type = FlexibleForeignKey("channels.VoteType", on_delete=models.CASCADE, blank=False)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)


# Doing this as a Many to Many so I can use BigInts
class ShowPlayer(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    player = FlexibleForeignKey("players.Player", on_delete=models.CASCADE, blank=False)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)
    used = models.BooleanField(default=False, blank=False)


class ShowVoteTypePlayerPool(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    player = FlexibleForeignKey("players.Player", on_delete=models.CASCADE, blank=False)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)
    vote_type = FlexibleForeignKey("channels.VoteType", on_delete=models.CASCADE, blank=False)
    used = models.BooleanField(default=False, blank=False)


class Suggestion(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=True, null=True)
    suggestion_pool = FlexibleForeignKey("channels.SuggestionPool", on_delete=models.CASCADE, blank=False)
    used = models.BooleanField(default=False, blank=False)
    voted_on = models.NullBooleanField(default=False, blank=True)
    amount_voted_on = models.IntegerField(default=0, blank=True, null=True)
    value = models.CharField(blank=False, max_length=255)
    # Pre-show upvotes
    preshow_value = models.IntegerField(default=0, blank=False)
    session_id = models.CharField(blank=True, null=True, max_length=255)
    user = models.ForeignKey(User, blank=True, null=True)

    created = models.DateTimeField(blank=False)

    def __unicode__(self):
        return self.value


class PreshowVote(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=True, null=True)
    suggestion = FlexibleForeignKey("Suggestion", on_delete=models.CASCADE, blank=False)
    session_id = models.CharField(blank=True, null=True, max_length=255)
    user = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        # Count all the preshow votes for the suggestion
        preshow_count = PreshowVote.objects.filter(suggestion=self.suggestion).count()
        # Then add the new vote to that count
        self.suggestion.preshow_value = preshow_count + 1
        self.suggestion.save()
        super(PreshowVote, self).save(*args, **kwargs)


class LiveVote(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    vote_option = FlexibleForeignKey("VoteOption", on_delete=models.CASCADE, blank=False, null=False)

    session_id = models.CharField(blank=False, max_length=255)
    user = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return str(self.id)

class ShowInterval(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)
    vote_type = FlexibleForeignKey("channels.VoteType", on_delete=models.CASCADE, blank=False)
    interval = models.IntegerField(blank=True, null=True)
    player = FlexibleForeignKey("players.Player", on_delete=models.CASCADE, blank=True, null=True)

    def __unicode__(self):
        return str(self.id)


class VoteOption(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    option_number = models.IntegerField(blank=False, null=False)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)
    vote_type = FlexibleForeignKey("channels.VoteType", on_delete=models.CASCADE, blank=False)
    interval = models.IntegerField(blank=True, null=True)
    suggestion = FlexibleForeignKey("Suggestion", on_delete=models.CASCADE, blank=True, null=True)
    player = FlexibleForeignKey("players.Player", on_delete=models.CASCADE, blank=True, null=True)


    def __unicode__(self):
        return str(self.id)


class VotedItem(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)
    vote_type = FlexibleForeignKey("channels.VoteType", on_delete=models.CASCADE, blank=False)
    vote_option = FlexibleForeignKey("VoteOption", on_delete=models.CASCADE, blank=False, null=False)
    interval = models.IntegerField(default=None, blank=True, null=True)

    def __unicode__(self):
        return str(self.id)
