from players.models import Player
from rest_framework import viewsets
from players.serializers import PlayerSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows players to be viewed or edited.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer