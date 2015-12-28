from django.contrib import admin
from shows.models import (Show, Suggestion, PreshowVote, LiveVote,
                          ShowInterval, VoteOptions, VotedItem)


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'archived')


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'value', 'show', 'suggestion_pool', 'user')
    list_display_links = ('id',)
    search_fields = ['show__id']


@admin.register(PreshowVote)
class PreshowVoteAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveVote)
class LiveVoteAdmin(admin.ModelAdmin):
    pass


@admin.register(ShowInterval)
class ShowIntervalAdmin(admin.ModelAdmin):
    pass


@admin.register(VoteOptions)
class VoteOptionsAdmin(admin.ModelAdmin):
    pass


@admin.register(VotedItem)
class VotedItemAdmin(admin.ModelAdmin):
    pass
