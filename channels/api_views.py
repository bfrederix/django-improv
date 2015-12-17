from rest_framework import viewsets

from channels.models import Channel, ChannelAddress
from channels.serializers import ChannelSerializer, ChannelAddressSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Channels
    """
    model = Channel
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()


class ChannelAddressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Channel Addresses
    """
    model = ChannelAddress
    serializer_class = ChannelAddressSerializer
    queryset = ChannelAddress.objects.all()