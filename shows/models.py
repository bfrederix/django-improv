from django.db import models

from utilities.fields import BoundedBigAutoField, FlexibleForeignKey


VOTE_STYLE = [('player-options', 'Player Options'),
              ('player-pool', 'Player Pool'),
              ('options', 'Options'),
              ('preshow-voted', 'Pre-show Voted'),
              ('all-players', 'All Players'),
              ('test', 'Test')]
OCCURS_TYPE = [('during', 'During'),
               ('before', 'Before')]

LEVEL_POINT = 30


class SuggestionPool(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=100)
    display_name = models.CharField(blank=False, max_length=100)
    description = models.TextField(blank=False)

    created = models.DateTimeField(auto_now_add=True, blank=False)

'''
    @property
    def delete_all_suggestions_and_live_votes(self):
        # Get all the pools suggestions
        suggestions = Suggestion.query(Suggestion.suggestion_pool == self.key,
                                       ).fetch(keys_only=True)
        # Get all the live votes for that suggestion
        for suggestion in suggestions:
            live_votes = LiveVote.query(LiveVote.suggestion == suggestion,
                                        ).fetch(keys_only=True)
            # Delete the live votes
            models.delete_multi(live_votes)
        # Delete all the pool suggestions
        models.delete_multi(suggestions)
'''


class VoteType(models.Model):
    # Defined at creation
    id = BoundedBigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=100)
    display_name = models.CharField(blank=False, max_length=100)
    suggestion_pool = FlexibleForeignKey("SuggestionPool", blank=False)
    preshow_voted = models.BooleanField(blank=False, default=False)
    has_intervals = models.BooleanField(blank=False, default=False)
    interval_uses_players = models.BooleanField(blank=False, default=False)
    intervals = models.CommaSeparatedIntegerField(blank=True, max_length=100)
    style = models.CharField(choices=VOTE_STYLE, blank=False, max_length=100)
    occurs = models.CharField(choices=OCCURS_TYPE, blank=False, max_length=100)
    ordering = models.IntegerField(default=0, blank=False)
    options = models.IntegerField(default=3, blank=False)
    randomize_amount = models.IntegerField(default=6, blank=False)
    button_color = models.CharField(default="#003D7A", blank=False, max_length=100)

    # Dynamic
    current_interval = models.IntegerField(blank=True, null=True)
    current_init = models.DateTimeField(blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=False)


class Show(models.Model):
    # Assigned to show on creation
    id = BoundedBigAutoField(primary_key=True)
    vote_length = models.IntegerField(default=25, blank=False)
    result_length = models.IntegerField(default=10, blank=False)
    vote_options = models.IntegerField(default=3, blank=False)
    timezone = models.CharField(default='America/Denver', blank=False, max_length=100)

    created = models.DateTimeField(auto_now_add=True, blank=False)
    archived = models.BooleanField(default=False, blank=False)

    # Changes during live show
    current_vote_type = FlexibleForeignKey("VoteType", blank=True, related_name='+',
                                           null=True)
    current_vote_init = models.DateTimeField(blank=True, null=True)
    recap_type = FlexibleForeignKey("VoteType", blank=True, related_name='+',
                                    null=True)
    recap_init = models.DateTimeField(blank=True, null=True)
    locked = models.BooleanField(default=False, blank=False)

    # Perhaps fetch all vote types by show id here
    # vote_types =

    # Perhaps fetch all players by show id here
    # players =

    # Perhaps fetch the player pool by show id here
    # player_pool =


# Doing this as a Many to Many so I can use BigInts
class ShowVoteType(models.Model):
    vote_type = FlexibleForeignKey("VoteType", blank=False)
    show = FlexibleForeignKey("Show", blank=False)


# Doing this as a Many to Many so I can use BigInts
class ShowPlayer(models.Model):
    player = FlexibleForeignKey("players.Player", blank=False)
    show = FlexibleForeignKey("Show", blank=False)


# Doing this as a Many to Many so I can use BigInts
# These can be deleted throughout the show to decrease the pool size
class ShowPlayerPool(models.Model):
    player = FlexibleForeignKey("players.Player", blank=False)
    show = FlexibleForeignKey("Show", blank=False)


class Suggestion(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", blank=True, null=True)
    suggestion_pool = FlexibleForeignKey("SuggestionPool", blank=False)
    used = models.BooleanField(default=False, blank=False)
    voted_on = models.NullBooleanField(default=False, blank=True)
    amount_voted_on = models.IntegerField(default=0, blank=True, null=True)
    value = models.CharField(blank=False, max_length=255)
    # Pre-show upvotes
    preshow_value = models.IntegerField(default=0, blank=True, null=True)
    session_id = models.CharField(blank=False, max_length=255)
    user_id = models.CharField(blank=True, null=True, max_length=100)

    created = models.DateTimeField(auto_now_add=True, blank=False)


class PreshowVote(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", blank=True, null=True)
    suggestion = FlexibleForeignKey("Suggestion", blank=False)
    session_id = models.CharField(blank=False, max_length=255)

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
    show = FlexibleForeignKey("Show", blank=False)
    vote_type = FlexibleForeignKey("VoteType", blank=False)
    player = FlexibleForeignKey("players.Player", blank=True, null=True)
    suggestion = FlexibleForeignKey("Suggestion", blank=True, null=True)
    interval = models.IntegerField(blank=True, null=True)
    session_id = models.CharField(blank=False, max_length=255)
    user_id = models.CharField(blank=True, null=True, max_length=100)


class ShowInterval(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", blank=False)
    vote_type = FlexibleForeignKey("VoteType", blank=False)
    interval = models.IntegerField(blank=False)
    player = FlexibleForeignKey("players.Player", blank=True, null=True)


# Doing this as a Many to Many so I can use BigInts
class OptionList(models.Model):
    suggestion = FlexibleForeignKey("Suggestion", blank=False)
    vote_option = FlexibleForeignKey("VoteOptions", blank=False)


class VoteOptions(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    show = FlexibleForeignKey("Show", blank=False)
    vote_type = FlexibleForeignKey("VoteType", blank=False)
    interval = models.IntegerField(blank=True, null=True)

    # Perhaps fetch all suggestions by vote option here

class VotedItem(models.Model):
    id = BoundedBigAutoField(primary_key=True)
    vote_type = FlexibleForeignKey("VoteType", blank=False)
    show = FlexibleForeignKey("Show", blank=False)
    suggestion = FlexibleForeignKey("Suggestion", blank=True, null=True)
    player = FlexibleForeignKey("players.Player", blank=True, null=True)
    interval = models.IntegerField(default=None, blank=True, null=True)
