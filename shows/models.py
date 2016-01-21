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

    def formatted_date(self):
        return self.created.strftime(DATE_FORMAT_STR)

    def formatted_youtube(self):
        if self.embedded_youtube:
            return "https://www.youtube.com/embed/{0}".format(self.embedded_youtube)
        return ''

    # All vote types by show id
    def vote_types(self):
        return [svt.vote_type.id for svt in ShowVoteType.objects.filter(show=self.id)]

    # All players by show id
    def players(self):
        return [sp.player.id for sp in ShowPlayer.objects.filter(show=self.id)]

    # The remaining un-used players in the show player pool
    def remaining_show_players(self):
        return [sp.player.id for sp in ShowPlayer.objects.filter(show=self.id).exclude(used=True)]

    # The remaining un-used players in the show player pool
    def remaining_vote_type_players(self):
        if self.current_vote_type:
            return [svtpp.player.id \
                    for svtpp in ShowVoteTypePlayerPool.objects.filter(
                        show=self.id,
                        vote_type=self.current_vote_type).exclude(used=True)]
        else:
            return []

# Doing this as a Many to Many so I can use BigInts
class ShowVoteType(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    vote_type = FlexibleForeignKey("channels.VoteType", blank=False)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)


# Doing this as a Many to Many so I can use BigInts
class ShowPlayer(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    player = FlexibleForeignKey("players.Player", blank=False)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)
    used = models.BooleanField(default=False, blank=False)


class ShowVoteTypePlayerPool(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    player = FlexibleForeignKey("players.Player", blank=False)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)
    vote_type = FlexibleForeignKey("channels.VoteType", blank=False)
    used = models.BooleanField(default=False, blank=False)


class Suggestion(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    channel = FlexibleForeignKey("channels.Channel", blank=False)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=True, null=True)
    suggestion_pool = FlexibleForeignKey("channels.SuggestionPool", blank=False)
    used = models.BooleanField(default=False, blank=False)
    voted_on = models.NullBooleanField(default=False, blank=True)
    amount_voted_on = models.IntegerField(default=0, blank=True, null=True)
    value = models.CharField(blank=False, max_length=255)
    # Pre-show upvotes
    preshow_value = models.IntegerField(default=0, blank=True, null=True)
    session_id = models.CharField(blank=False, max_length=255)
    user = models.ForeignKey(User, blank=True, null=True)

    created = models.DateTimeField(blank=False)

    def __unicode__(self):
        return self.value

class PreshowVote(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=True, null=True)
    suggestion = FlexibleForeignKey("Suggestion", blank=False)
    session_id = models.CharField(blank=False, max_length=255)

    def __unicode__(self):
        return str(self.id)

'''
    def put(self, *args, **kwargs):
        """Increment the Suggestion's pre-show value"""
        if self.suggestion:
            suggestion_entity = self.suggestion.get()
            suggestion_entity.preshow_value += 1
            suggestion_entity.put()
        return super(PreshowVote, self).put(*args, **kwargs)
'''


class LiveVote(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)
    vote_type = FlexibleForeignKey("channels.VoteType", blank=False)
    player = FlexibleForeignKey("players.Player", blank=True, null=True)
    suggestion = FlexibleForeignKey("Suggestion", blank=True, null=True)
    interval = models.IntegerField(blank=True, null=True)
    session_id = models.CharField(blank=False, max_length=255)
    user = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return str(self.id)

class ShowInterval(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)
    vote_type = FlexibleForeignKey("channels.VoteType", blank=False)
    interval = models.IntegerField(blank=False)
    player = FlexibleForeignKey("players.Player", blank=True, null=True)

    def __unicode__(self):
        return str(self.id)

class VoteOptions(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)
    vote_type = FlexibleForeignKey("channels.VoteType", blank=False)
    interval = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return str(self.id)
    # Perhaps fetch all suggestions by vote option here


class OptionSuggestion(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    suggestion = FlexibleForeignKey("Suggestion", blank=False)
    vote_option = FlexibleForeignKey("VoteOptions", blank=False)


class VotedItem(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", on_delete=models.CASCADE, blank=False)
    vote_type = FlexibleForeignKey("channels.VoteType", blank=False)
    suggestion = FlexibleForeignKey("Suggestion", blank=True, null=True)
    player = FlexibleForeignKey("players.Player", blank=True, null=True)
    interval = models.IntegerField(default=None, blank=True, null=True)

    def __unicode__(self):
        return str(self.id)
