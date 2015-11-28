from rest_framework import serializers

from shows.models import Show


class ShowSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Show
        fields = ('id', 'channel', 'timezone', 'created',
                  #'current_vote_type', 'current_vote_init',
                  'locked', 'winners_photo_link', 'embedded_youtube')