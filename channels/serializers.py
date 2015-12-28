from rest_framework import serializers

from channels.models import Channel, ChannelAddress, SuggestionPool


class ChannelAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChannelAddress
        fields = ('id', 'street', 'city', 'state',
                  'zipcode')


class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    address = ChannelAddressSerializer(read_only=True)

    class Meta:
        model = Channel
        fields = ('id', 'name', 'display_name', 'is_premium',
                  'short_description', 'description',
                  'thumbnail_url', 'logo_url', 'team_photo_url',
                  'website', 'facebook_page', 'address',
                  'buy_tickets_link', 'next_show', 'timezone')


class SuggestionPoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuggestionPool
        fields = ('id', 'channel', 'name', 'display_name',
                  'description', 'max_user_suggestions', 'active',
                  'admin_only', 'created')