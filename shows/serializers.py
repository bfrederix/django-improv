from rest_framework import serializers

from shows.models import Show


class ShowSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source="formatted_date")
    channel_id = serializers.IntegerField()
    channel_name = serializers.CharField()
    created = serializers.DateTimeField()
    locked = serializers.BooleanField()
    photo_link = serializers.CharField(required=False)
    embedded_youtube = serializers.CharField(required=False)

    class Meta:
        fields = ('id', 'channel_id', 'channel_name',
                  'name', 'created',
                  #'current_vote_type', 'current_vote_init',
                  'locked', 'photo_link', 'embedded_youtube')


class SuggestionsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    created = serializers.DateTimeField()
    used = serializers.BooleanField()
    points = serializers.IntegerField()
    voted_on = serializers.BooleanField()
    value = serializers.CharField()
    user_id = serializers.IntegerField()

    class Meta:
        fields = ('id', 'created', 'used', 'points',
                  'voted_on', 'value', 'user_id')