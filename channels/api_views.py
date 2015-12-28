from rest_framework import viewsets
from rest_framework.response import Response

from channels.models import Channel, ChannelAddress, SuggestionPool
from channels.serializers import (ChannelSerializer, ChannelAddressSerializer,
                                  SuggestionPoolSerializer)
from channels import service as channels_service


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


class SuggestionPoolViewSet(viewsets.ViewSet):
    """
    API endpoint that allows suggestion pools to be viewed
    """

    def retrieve(self, request, pk=None):
        suggestion_pool = channels_service.suggestion_pool_or_404(pk)
        serializer = SuggestionPoolSerializer(suggestion_pool)
        return Response(serializer.data)

    def list(self, request):
        kwargs = {}
        channel_id = self.request.query_params.get('channel_id')
        sort_by_active = self.request.query_params.get('sort_by_active')
        if channel_id:
            kwargs['channel'] = channel_id
        queryset = SuggestionPool.objects.filter(**kwargs)
        if sort_by_active:
            queryset = queryset.order_by('-active', 'name')
        serializer = SuggestionPoolSerializer(queryset, many=True)
        return Response(serializer.data)