from rest_framework import viewsets
from rest_framework.response import Response

from channels.models import (Channel, ChannelAddress, SuggestionPool,
                             VoteType, VOTE_STYLE)
from channels.serializers import (ChannelSerializer, ChannelAddressSerializer,
                                  SuggestionPoolSerializer, VoteTypeSerializer,
                                  VoteStyleSerializer)
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
        active_only = self.request.query_params.get('active_only')
        if channel_id:
            kwargs['channel'] = channel_id
        queryset = SuggestionPool.objects.filter(**kwargs)
        # Exclude non-active suggestion pools
        if active_only:
            queryset = queryset.exclude(active=False)
        if sort_by_active:
            queryset = queryset.order_by('-active', 'name')
        serializer = SuggestionPoolSerializer(queryset, many=True)
        return Response(serializer.data)


class VoteTypeViewSet(viewsets.ViewSet):
    """
    API endpoint that allows vote types to be viewed
    """

    def retrieve(self, request, pk=None):
        vote_type = channels_service.vote_type_or_404(pk)
        serializer = VoteTypeSerializer(vote_type)
        return Response(serializer.data)

    def list(self, request):
        kwargs = {}
        channel_id = self.request.query_params.get('channel_id')
        sort_by_active = self.request.query_params.get('sort_by_active')
        active_only = self.request.query_params.get('active_only')
        if channel_id:
            kwargs['channel'] = channel_id
        queryset = VoteType.objects.filter(**kwargs)
        # Exclude non-active suggestion pools
        if active_only:
            queryset = queryset.exclude(active=False)
        if sort_by_active:
            queryset = queryset.order_by('-active', 'name')
        serializer = VoteTypeSerializer(queryset, many=True)
        return Response(serializer.data)


class VoteStyleViewSet(viewsets.ViewSet):
    """
    API endpoint that allows vote styles to be viewed
    """

    def retrieve(self, request, pk=None):
        style_id = int(pk)
        vote_style = channels_service.vote_style_or_404(style_id)
        style_dict = {'id': style_id, 'name': vote_style[1]}
        serializer = VoteStyleSerializer(style_dict)
        return Response(serializer.data)

    def list(self, request):
        vote_styles = []
        count = 0
        for (name, display_name) in VOTE_STYLE:
            count +=1
            vote_styles.append({'id': count, 'name': display_name})
        serializer = VoteStyleSerializer(vote_styles, many=True)
        return Response(serializer.data)