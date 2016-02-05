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
    points = serializers.IntegerField()
    voted_on = serializers.BooleanField()
    value = serializers.CharField()
    preshow_value = serializers.IntegerField()
    user_id = serializers.IntegerField()
    session_id = serializers.CharField(required=False)
    user_already_upvoted = serializers.BooleanField()

    class Meta:
        fields = ('id', 'created', 'used', 'points',
                  'voted_on', 'value', 'preshow_value',
                  'user_id', 'session_id', 'user_already_upvoted')


class VoteOptionSerializer(serializers.Serializer):
    suggestion_id = serializers.IntegerField()
    used = serializers.BooleanField()
    suggestion = serializers.CharField()
    user_id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=False)

    class Meta:
        fields = ('show', 'vote_type', 'interval',
                  'suggestion', 'player')


class LiveVoteSerializer(serializers.Serializer):
    count = serializers.IntegerField()

    class Meta:
        fields = ('count',)