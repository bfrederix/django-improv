from leaderboards.models import LeaderboardSpan, Medal
from rest_framework import serializers


class LeaderboardEntrySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    channel_name = serializers.CharField()
    show = serializers.IntegerField()
    username = serializers.CharField()
    points = serializers.IntegerField()
    wins = serializers.IntegerField()
    medals = serializers.ListField()

    class Meta:
        fields = ('id', 'user_id', 'channel_name', 'show',
                  'username', 'points', 'wins', 'medals')


class LeaderboardEntrySpanSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    channel_name = serializers.CharField()
    username = serializers.CharField()
    show_wins = serializers.IntegerField()
    points = serializers.IntegerField()
    suggestion_wins = serializers.IntegerField()

    class Meta:
        fields = ('user_id', 'channel_name', 'username',
                  'show_wins', 'points', 'suggestion_wins')


class LeaderboardSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    points = serializers.IntegerField(required=False)
    suggestion_wins = serializers.IntegerField(required=False)
    show_wins = serializers.IntegerField(required=False)

    class Meta:
        fields = ('user_id', 'username',
                  'points', 'suggestion_wins', 'show_wins',)


class LeaderboardSpanSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaderboardSpan
        fields = ('id', 'channel', 'name',
                  'start_date', 'end_date',
                  'created')


class MedalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medal
        fields = ('id', 'name', 'display_name',
                  'description', 'image_filename',
                  'icon_filename')