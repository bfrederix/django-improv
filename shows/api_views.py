from rest_framework import viewsets

from shows.models import Show
from shows.serializers import ShowSerializer


class ShowViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows voteprov users to be viewed or edited.
    """
    model = Show
    serializer_class = ShowSerializer
    queryset = Show.objects.all()