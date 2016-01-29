from rest_framework import viewsets
from rest_framework.response import Response

from shows.models import Show, Suggestion, LiveVote, PreshowVote
from shows.serializers import ShowSerializer, SuggestionsSerializer
from shows import service as shows_service
from utilities.api import APIObject


class ShowAPIObject(APIObject):
    field_list = ['id',
                  'created',
                  'locked',
                  'show_length',
                  'photo_link',
                  'embedded_youtube',
                  'formatted_youtube',
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
                  'value',
                  'preshow_value',
                  'session_id']

    def __init__(self, suggestion, **kwargs):
        super(SuggestionAPIObject, self).__init__(suggestion, **kwargs)
        self.points = LiveVote.objects.filter(suggestion=suggestion).count()
        user = getattr(suggestion, 'user', None)
        if user:
            self.user_id = user.id
        else:
            self.user_id = None
        upvote_user_id = kwargs.get('upvote_user_id')
        upvote_session_id = kwargs.get('upvote_session_id')
        if upvote_user_id and upvote_user_id !="None":
            self.user_already_upvoted = bool(PreshowVote.objects.filter(show=suggestion.show,
                                                                        suggestion=suggestion,
                                                                        user=upvote_user_id).count())
        elif upvote_session_id and upvote_session_id !="None":
            self.user_already_upvoted = bool(PreshowVote.objects.filter(show=suggestion.show,
                                                                        suggestion=suggestion,
                                                                        session_id=upvote_session_id).count())
        else:
            self.user_already_upvoted = False


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
        api_kwargs = {'upvote_user_id': self.request.query_params.get('upvote_user_id'),
                      'upvote_session_id': self.request.query_params.get('upvote_session_id')}
        user_id = self.request.query_params.get('user_id')
        show_id = self.request.query_params.get('show_id')
        suggestion_pool_id = self.request.query_params.get('suggestion_pool_id')
        suggestion_pool_sort = self.request.query_params.get('suggestion_pool_sort')
        if user_id:
            kwargs['user'] = user_id
        if show_id:
            kwargs['show'] = show_id
        if suggestion_pool_id:
            kwargs['suggestion_pool'] = suggestion_pool_id
        queryset = Suggestion.objects.filter(**kwargs)
        # If we need to sort the suggestions for a suggestion pool display
        if suggestion_pool_sort:
            queryset = queryset.order_by('-preshow_value', 'created')
        updated_suggestions = [SuggestionAPIObject(item, **api_kwargs) for item in queryset]
        serializer = SuggestionsSerializer(updated_suggestions, many=True)
        return Response(serializer.data)