from django.shortcuts import get_object_or_404

from players.models import Player


def player_or_404(player_id):
    return get_object_or_404(Player, id=player_id)