from rest_framework import viewsets
from rest_framework.response import Response

from shows.models import Show, Suggestion, LiveVote
from shows.serializers import ShowSerializer, SuggestionsSerializer
from shows import service as shows_service
from utilities.api import APIObject


class SuggestionAPIObject(APIObject):
    field_list = ['id',
                  'created',
                  'used',
                  'voted_on',
                  'value']

    def __init__(self, suggestion, **kwargs):
        super(SuggestionAPIObject, self).__init__(suggestion, **kwargs)
        self.points = LiveVote.objects.filter(suggestion=suggestion).count()
        self.user_id = suggestion.user.id


class ShowViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows voteprov users to be viewed or edited.
    """
    model = Show
    serializer_class = ShowSerializer
    queryset = Show.objects.all()


class SuggestionViewSet(viewsets.ViewSet):
    """
    API endpoint that allows voteprov users to be viewed or edited.
    """

    def retrieve(self, request, pk=None):
        suggestion = shows_service.suggestion_or_404(pk)
        suggestion_api_obj = SuggestionAPIObject(suggestion)
        serializer = SuggestionsSerializer(suggestion_api_obj)
        return Response(serializer.data)

    def list(self, request):
        kwargs = {}
        user_id = self.request.query_params.get('user_id')
        show_id = self.request.query_params.get('show_id')
        if user_id:
            kwargs['user'] = user_id
        if show_id:
            kwargs['show'] = show_id
        queryset = Suggestion.objects.filter(**kwargs)
        updated_suggestions = [SuggestionAPIObject(item) for item in queryset]
        serializer = SuggestionsSerializer(updated_suggestions, many=True)
        return Response(serializer.data)