from rest_framework import viewsets
from rest_framework.response import Response

from recaps.serializers import RecapSerializer
from shows import service as shows_service
from users import service as users_service
from utilities.api import APIObject


class RecapAPIObject(APIObject):

    def __init__(self, voted_item, **kwargs):
        super(RecapAPIObject, self).__init__(voted_item, **kwargs)
        # Get all the options for that vote
        self.vote_option_ids = shows_service.fetch_vote_option_ids(show_id=voted_item.show_id,
                                                              vote_type_id=voted_item.vote_type_id,
                                                              interval=voted_item.interval)
        # if there's a player attached to the vote option
        if voted_item.player_id:
            self.player = voted_item.player_id
        # If the voted item was on a suggestions
        if voted_item.suggestion_id:
            self.winning_suggestion = voted_item.suggestion_id
        # If it was an interval
        if voted_item.interval is not None:
            self.interval = voted_item.interval
        self.vote_type = voted_item.vote_type.display_name


class RecapViewSet(viewsets.ViewSet):
    """
    API endpoint that returns leaderboard entries
    """

    def retrieve(self, request, pk=None):
        voted_items = shows_service.fetch_voted_items_by_show(pk,
                                                              ordered=True)
        recaps = [RecapAPIObject(item) for item in voted_items]
        serializer = RecapSerializer(recaps, many=True)
        return Response(serializer.data)
