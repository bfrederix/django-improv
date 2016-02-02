from rest_framework import viewsets
from rest_framework.response import Response

from recaps.serializers import RecapSerializer, OptionSuggestionSerializer
from shows import service as shows_service
from users import service as users_service
from utilities.api import APIObject


class RecapAPIObject(APIObject):

    def __init__(self, voted_item, **kwargs):
        super(RecapAPIObject, self).__init__(voted_item, **kwargs)
        # Get all the options for that vote
        vote_option_ids = shows_service.fetch_vote_option_ids(show_id=voted_item.show_id,
                                                              vote_type_id=voted_item.vote_type_id,
                                                              interval=voted_item.interval)
        try:
            # Get the id for the vote options if it exists
            self.options_id = vote_option_ids[0]
        except IndexError:
            pass
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


class OptionSuggestionAPIObject(APIObject):

    def __init__(self, option, **kwargs):
        super(OptionSuggestionAPIObject, self).__init__(option, **kwargs)
        self.suggestion_id = option.suggestion_id
        self.used = option.suggestion.used
        self.suggestion = option.suggestion.value
        user_id = option.suggestion.user_id
        if user_id:
            user_profile = users_service.fetch_user_profile(user_id)
            self.user_id = user_profile.user_id
            self.username = user_profile.safe_username


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


class VoteOptionsViewSet(viewsets.ViewSet):
    """
    API endpoint that returns leaderboard entries
    """

    def retrieve(self, request, pk=None):
        option_suggestions = shows_service.fetch_option_suggestion(pk)
        recaps = [OptionSuggestionAPIObject(item) for item in option_suggestions]
        serializer = OptionSuggestionSerializer(recaps, many=True)
        return Response(serializer.data)

    def list(self, request):
        pass