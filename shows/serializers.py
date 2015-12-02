from rest_framework import serializers

from shows.models import Show


class ShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Show
        fields = ('id', 'channel', 'timezone', 'created',
                  #'current_vote_type', 'current_vote_init',
                  'locked', 'winners_photo_link', 'embedded_youtube')


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