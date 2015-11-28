from rest_framework import viewsets

from channels.models import Channel
from channels.serializers import ChannelSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows voteprov users to be viewed or edited.
    """
    model = Channel
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()