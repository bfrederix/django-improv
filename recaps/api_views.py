from rest_framework import viewsets
from rest_framework.response import Response

from recaps.serializers import RecapSerializer
from shows import service as shows_service
from utilities.api import APIObject


class RecapAPIObject(APIObject):

    def __init__(self, voted_item, **kwargs):
        super(RecapAPIObject, self).__init__(voted_item, **kwargs)
        ### THIS COULD USE SOME CACHING ###
        # Get the show interval
        show_interval = shows_service.get_show_interval(voted_item.show_id,
                                                        voted_item.vote_type_id,
                                                        voted_item.interval)
        # Get all the options for that vote
        self.vote_options = shows_service.fetch_vote_option_ids(
                                   show_id=voted_item.show_id,
                                   vote_type_id=voted_item.vote_type_id,
                                   interval=voted_item.interval)
        # Get the vote type
        voted_vote_type = voted_item.vote_type
        # Get the voted option
        voted_option = voted_item.vote_option
        # Set the winning option
        self.winning_option = voted_option.id
        # if there's a player attached to the show interval
        if show_interval and show_interval.player_id:
            self.player = show_interval.player_id
        # else if there's a player attached to the voted option
        elif voted_option.player_id:
            self.player = voted_option.player_id
        # If it was an interval
        if voted_item.interval is not None:
            self.interval = voted_item.interval
        # Get the vote type display name
        self.vote_type = voted_vote_type.display_name
        # Get if the vote was a players only vote
        self.players_only = voted_vote_type.players_only


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
