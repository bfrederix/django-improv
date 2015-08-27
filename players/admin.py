from django.contrib import admin
from players.models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'name', 'photo_url', 'star', 'created')