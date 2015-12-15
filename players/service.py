import datetime
import pytz

from django.shortcuts import get_object_or_404

from players.models import Player


def player_or_404(player_id):
    return get_object_or_404(Player, id=player_id)


def create_player(name, channel_id, photo_url, active=True, star=False):
    player = Player(name=name,
                    channel=channel_id,
                    photo_url=photo_url,
                    active=active,
                    star=star,
                    created=datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
    player.save()
    return player