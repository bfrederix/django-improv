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
        vote_options = shows_service.fetch_vote_options(show=voted_item.show,
                                                        vote_type=voted_item.vote_type,
                                                        interval=voted_item.interval)
        try:
            # Get the list of suggestions for the vote option if they exist
            option_suggestions = shows_service.fetch_option_suggestion(vote_options[0].id)
        except IndexError:
            pass
        else:
            self.options = [OptionSuggestionAPIObject(item) for item in option_suggestions]
        # if there's a player attached to the vote option
        if voted_item.player:
            self.player = voted_item.player.id
        # If the voted item was on a suggestions
        if voted_item.suggestion:
            self.winning_suggestion = voted_item.suggestion.id
        # If it was an interval
        if voted_item.interval is not None:
            self.interval = voted_item.interval
        self.vote_type = voted_item.vote_type.display_name


class OptionSuggestionAPIObject(APIObject):

    def __init__(self, option, **kwargs):
        super(OptionSuggestionAPIObject, self).__init__(option, **kwargs)
        self.suggestion_id = option.suggestion.id
        self.used = option.suggestion.used
        self.suggestion = option.suggestion.value
        user = option.suggestion.user
        if user:
            user_profile = users_service.fetch_user_profile(user.id)
            self.user_id = user_profile.user_id
            self.username = user_profile.safe_username


class RecapViewSet(viewsets.ViewSet):
    """
    API endpoint that returns leaderboard entries
    """

    def retrieve(self, request, pk=None):
        show = shows_service.show_or_404(pk)
        voted_items = shows_service.fetch_voted_items_by_show(show.id,
                                                              ordered=True)
        recaps = [RecapAPIObject(item) for item in voted_items]
        serializer = RecapSerializer(recaps, many=True)
        return Response(serializer.data)