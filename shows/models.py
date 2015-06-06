from django.db import models

VOTE_STYLE = ['player-options', 'player-pool', 'options',
              'preshow-voted', 'all-players', 'test']
OCCURS_TYPE = ['during', 'before']

LEVEL_POINT = 30


class SuggestionPool(models.Model):
    name = models.CharField(blank=False)
    display_name = models.CharField(blank=False)
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

    def put(self, *args, **kwargs):
        if not self.created:
            self.created = get_mountain_time()
        return super(SuggestionPool, self).put(*args, **kwargs)
'''


class VoteType(models.Model):
    # Defined at creation
    name = models.CharField(blank=False)
    display_name = models.CharField(blank=False)
    suggestion_pool = models.ForeignKey("SuggestionPool", blank=False)
    preshow_voted = models.BooleanField(blank=False, default=False)
    has_intervals = models.BooleanField(blank=False, default=False)
    interval_uses_players = models.BooleanField(blank=False, default=False)
    intervals = models.CommaSeparatedIntegerField(blank=True)
    style = models.CharField(choices=VOTE_STYLE, blank=False)
    occurs = models.CharField(choices=OCCURS_TYPE, blank=False)
    ordering = models.IntegerField(default=0, blank=False)
    options = models.IntegerField(default=3, blank=False)
    randomize_amount = models.IntegerField(default=6, blank=False)
    button_color = models.CharField(default="#003D7A", blank=False)

    # Dynamic
    current_interval = models.IntegerField(blank=True)
    current_init = models.DateTimeField(blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=False)


class Show(models.Model):
    # Assigned to show on creation
    vote_length = models.IntegerField(default=25, blank=False)
    result_length = models.IntegerField(default=10, blank=False)
    vote_options = models.IntegerField(default=3, blank=False)
    timezone = models.CharField(default='America/Denver', blank=False)
    vote_types = models.ManyToManyField("VoteType", blank=False)
    # All players in the show
    players = models.ManyToManyField("Player", blank=True)
    # Finite amount of players to select from during the show
    player_pool = models.ManyToManyField("Player", blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    archived = models.BooleanField(default=False, blank=False)

    # Changes during live show
    current_vote_type = models.ForeignKey("VoteType", blank=True)
    current_vote_init = models.DateTimeField(blank=True)
    recap_type = models.ForeignKey("VoteType", blank=True)
    recap_init = models.DateTimeField(blank=True)
    locked = models.BooleanField(default=False, blank=False)


class Suggestion(models.Model):
    show = models.ForeignKey("Show", blank=True)
    suggestion_pool = models.ForeignKey("SuggestionPool", blank=False)
    used = models.BooleanField(default=False, blank=True)
    voted_on = models.NullBooleanField(default=False, blank=True)
    amount_voted_on = models.IntegerField(default=0, blank=True)
    value = models.CharField(blank=False)
    # Pre-show upvotes
    preshow_value = models.IntegerField(default=0, blank=True)
    session_id = models.CharField(blank=False)
    user_id = models.BigIntegerField(blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=False)


class PreshowVote(models.Model):
    show = models.ForeignKey("Show", blank=True)
    suggestion = models.ForeignKey("Suggestion", blank=False)
    session_id = models.CharField(blank=False)

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
    show = models.ForeignKey("Show", blank=False)
    vote_type = models.ForeignKey("VoteType", blank=False)
    player = models.ForeignKey("Player", blank=True)
    suggestion = models.ForeignKey("Suggestion", blank=True)
    interval = models.IntegerField(blank=True)
    session_id = models.CharField(blank=False)
    user_id = models.BigIntegerField(default=None, blank=True)

'''
    def put(self, *args, **kwargs):
        """Increment the Suggestion's live value"""
        if self.suggestion:
            suggestion_entity = self.suggestion.get()
            # If the live vote included a suggestion
            if suggestion_entity:
                suggestion_entity.voted_on = True
                suggestion_entity.put()
        return super(LiveVote, self).put(*args, **kwargs)
'''


class ShowInterval(models.Model):
    show = models.ForeignKey("Show", blank=False)
    vote_type = models.ForeignKey("VoteType", blank=False)
    interval = models.IntegerField(blank=False)
    player = models.ForeignKey("Player", blank=True)


class VoteOptions(models.Model):
    show = models.ForeignKey("Show", blank=False)
    vote_type = models.ForeignKey("VoteType", blank=False)
    interval = models.IntegerField(blank=True)
    option_list = models.ManyToManyField("Suggestion", blank=True)


class VotedItem(models.Model):
    vote_type = models.ForeignKey("VoteType", blank=False)
    show = models.ForeignKey("Show", blank=False)
    suggestion = models.ForeignKey("Suggestion", blank=True)
    player = models.ForeignKey("Player", blank=True)
    interval = models.IntegerField(default=None, blank=True)
