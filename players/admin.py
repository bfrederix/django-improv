from django.contrib import admin
from players.models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'photo_filename', 'star', 'created')