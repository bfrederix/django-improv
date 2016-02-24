from rest_framework import serializers


class RecapSerializer(serializers.Serializer):
    vote_options = serializers.ListField()
    vote_type = serializers.CharField()
    player = serializers.IntegerField(required=False)
    winning_option = serializers.IntegerField()
    winning_player = serializers.IntegerField(required=False)
    interval = serializers.IntegerField(required=False)
    players_only = serializers.BooleanField()

    class Meta:
        fields = ('vote_options', 'vote_type', 'player',
                  'winning_option', 'winning_player',
                  'interval', 'players_only')