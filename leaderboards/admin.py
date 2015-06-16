from django.contrib import admin
from leaderboards.models import (Medal, LeaderboardEntry, LeaderboardSpan)


@admin.register(Medal)
class MedalAdmin(admin.ModelAdmin):
    pass


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    pass


@admin.register(LeaderboardSpan)
class LeaderboardSpanAdmin(admin.ModelAdmin):
    pass
