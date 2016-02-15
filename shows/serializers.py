from rest_framework import serializers

from shows.models import Show


class ShowSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source="formatted_date")
    channel_id = serializers.IntegerField()
    channel_name = serializers.CharField()
    created = serializers.DateTimeField()
    locked = serializers.BooleanField()
    show_length = serializers.IntegerField()
    photo_link = serializers.CharField(required=False)
    embedded_youtube = serializers.CharField(required=False, source="formatted_youtube")
    show_seconds_remaining = serializers.IntegerField()
    vote_types = serializers.ListField()
    current_display = serializers.CharField(required=False)
    current_vote_type = serializers.IntegerField(required=False)
    vote_options = serializers.ListField(required=False)

    class Meta:
        fields = ('id', 'channel_id', 'channel_name',
                  'name', 'created', 'show_length',
                  'vote_types',
                  'current_vote_type', 'current_display',
                  'locked', 'photo_link', 'embedded_youtube',
                  'show_seconds_remaining', 'vote_options')


class SuggestionsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    created = serializers.DateTimeField()
    used = serializers.BooleanField()
    voted_on = serializers.BooleanField()
    value = serializers.CharField()
    preshow_value = serializers.IntegerField()
    user_id = serializers.IntegerField()
    session_id = serializers.CharField(required=False)
    user_already_upvoted = serializers.BooleanField()

    class Meta:
        fields = ('id', 'created', 'used',
                  'voted_on', 'value', 'preshow_value',
                  'user_id', 'session_id', 'user_already_upvoted')


class VoteOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    show = serializers.IntegerField(source='show_id')
    vote_type = serializers.IntegerField(source='vote_type_id')
    option_number = serializers.IntegerField()
    used = serializers.BooleanField(required=False)
    suggestion = serializers.IntegerField(required=False, source='suggestion_id')
    suggestion_value = serializers.CharField(required=False)
    player = serializers.IntegerField(required=False, source='player_id')
    player_name = serializers.CharField(required=False)
    player_photo = serializers.CharField(required=False)
    user_id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=False)
    live_votes = serializers.IntegerField()

    class Meta:
        fields = ('id', 'show', 'vote_type', 'interval',
                  'option_number', 'suggestion', 'suggestion_value',
                  'player', 'player_name', 'player_photo',
                  'user_id', 'username', 'live_votes',
                  'used')


class LiveVoteSerializer(serializers.Serializer):
    count = serializers.IntegerField()

    class Meta:
        fields = ('count',)