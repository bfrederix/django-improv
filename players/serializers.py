from players.models import Player
from rest_framework import serializers


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ('id', 'channel', 'name', 'photo_url', 'active', 'star', 'created')