from rest_framework import viewsets
from rest_framework.response import Response

from shows.models import Show, Suggestion, LiveVote
from shows.serializers import ShowSerializer, SuggestionsSerializer
from shows import service as shows_service
from utilities.api import APIObject


class ShowAPIObject(APIObject):
    field_list = ['id',
                  'created',
                  'locked',
                  'photo_link',
                  'embedded_youtube',
                  'formatted_date']

    def __init__(self, show, **kwargs):
        super(ShowAPIObject, self).__init__(show, **kwargs)
        self.channel_id = show.channel.id
        self.channel_name = show.channel.name


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


class ShowViewSet(viewsets.ViewSet):
    """
    API endpoint that allows shows to be viewed
    """

    def retrieve(self, request, pk=None):
        show = shows_service.show_or_404(pk)
        show_api_obj = ShowAPIObject(show)
        serializer = ShowSerializer(show_api_obj)
        return Response(serializer.data)

    def list(self, request):
        kwargs = {}
        channel_id = self.request.query_params.get('channel_id')
        order_by_date = self.request.query_params.get('order_by_date')
        # Filtering
        if channel_id:
            kwargs['channel'] = channel_id
        queryset = Show.objects.filter(**kwargs)
        # Ordering
        if order_by_date:
            queryset = queryset.order_by('-created')
        updated_shows = [ShowAPIObject(item) for item in queryset]
        serializer = ShowSerializer(updated_shows, many=True)
        return Response(serializer.data)


class SuggestionViewSet(viewsets.ViewSet):
    """
    API endpoint that allows suggestions to be viewed
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