from players.models import Player
from rest_framework import serializers


class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'channel', 'name', 'photo_url', 'star', 'created')