from leaderboards.models import LeaderboardEntry, Medal
from rest_framework import serializers


class LeaderboardEntrySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = LeaderboardEntry
        fields = ('id', 'user_id', 'show', 'username', 'points', 'wins')


class MedalSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Medal
        fields = ('id', 'name', 'display_name',
                  'description', 'image_filename',
                  'icon_filename')