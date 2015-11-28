from rest_framework import serializers

from channels.models import Channel


class ChannelSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Channel
        fields = ('id', 'name', 'display_name', 'is_premium',
                  'short_description', 'description',
                  'thumbnail_url', 'logo_url', 'team_photo_url',
                  'website', 'facebook_page', 'buy_tickets_link',
                  'next_show')