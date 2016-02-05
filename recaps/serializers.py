from rest_framework import serializers


class RecapSerializer(serializers.Serializer):
    options_id = serializers.IntegerField()
    vote_type = serializers.CharField()
    player = serializers.IntegerField(required=False)
    winning_suggestion = serializers.IntegerField(required=False)
    winning_player = serializers.IntegerField(required=False)
    interval = serializers.IntegerField(required=False)

    class Meta:
        fields = ('options', 'vote_type', 'player',
                  'winning_suggestion', 'winning_player',
                  'interval')