from rest_framework import viewsets
from rest_framework.response import Response

from players.models import Player
from players.serializers import PlayerSerializer
from players import service as players_service


class PlayerViewSet(viewsets.ViewSet):
    """
    API endpoint that allows players to be viewed
    """

    def retrieve(self, request, pk=None):
        player = players_service.player_or_404(pk)
        serializer = PlayerSerializer(player)
        return Response(serializer.data)

    def list(self, request):
        kwargs = {}
        channel_id = self.request.query_params.get('channel_id')
        sort_by_active = self.request.query_params.get('sort_by_active')
        active_only = self.request.query_params.get('active_only')
        if channel_id:
            kwargs['channel'] = channel_id
        queryset = Player.objects.filter(**kwargs).exclude(archived=True)
        # If we should sort by whether the user is active or not
        if sort_by_active:
            queryset = queryset.order_by('-active', 'star')
        # If we only want active users
        elif active_only:
            queryset = queryset.exclude(active=False).order_by('star')
        serializer = PlayerSerializer(queryset, many=True)
        return Response(serializer.data)