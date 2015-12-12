from rest_framework import serializers


class OptionSuggestionSerializer(serializers.Serializer):
    suggestion_id = serializers.IntegerField()
    used = serializers.BooleanField()
    suggestion = serializers.CharField()
    user_id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=False)

    class Meta:
        fields = ('option_list', 'vote_type', 'player',
                  'winning_suggestion')


class RecapSerializer(serializers.Serializer):
    options = OptionSuggestionSerializer(many=True, read_only=True, required=False)
    vote_type = serializers.CharField()
    player = serializers.IntegerField(required=False)
    winning_suggestion = serializers.IntegerField(required=False)
    interval = serializers.IntegerField(required=False)

    class Meta:
        fields = ('options', 'vote_type', 'player',
                  'winning_suggestion', 'interval')