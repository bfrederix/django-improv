from rest_framework import viewsets

from leaderboards.models import LeaderboardEntry, Medal
from leaderboards.serializers import LeaderboardEntrySerializer, MedalSerializer


class LeaderboardEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows voteprov users to be viewed or edited.
    """
    model = LeaderboardEntry
    serializer_class = LeaderboardEntrySerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = LeaderboardEntry.objects.all()
        user_id = self.request.query_params.get('user_id')
        order_by_show_date = self.request.query_params.get('order_by_show_date')
        if user_id:
            #import pdb;pdb.set_trace()
            queryset = queryset.filter(user=user_id)
        if order_by_show_date is not None:
            queryset = queryset.order_by('-show_date')
        return queryset


class MedalViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows voteprov users to be viewed or edited.
    """
    model = Medal
    serializer_class = MedalSerializer
    queryset = Medal.objects.all()