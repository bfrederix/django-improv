from leaderboards.models import LeaderboardEntry, Medal
from rest_framework import serializers


class LeaderboardEntrySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    channel_name = serializers.CharField()
    show = serializers.IntegerField()
    username = serializers.CharField()
    points = serializers.IntegerField()
    wins = serializers.IntegerField()

    class Meta:
        fields = ('id', 'user_id', 'channel_name', 'show', 'username', 'points', 'wins')


class LeaderboardSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    points = serializers.IntegerField()
    wins = serializers.IntegerField()
    suggestions = serializers.IntegerField(required=False)
    medals = serializers.ListField(required=False)

    class Meta:
        fields = ('user_id', 'username',
                  'points', 'wins', 'suggestions', 'medals',)


class MedalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medal
        fields = ('id', 'name', 'display_name',
                  'description', 'image_filename',
                  'icon_filename')