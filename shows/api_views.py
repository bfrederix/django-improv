import datetime
import pytz

from rest_framework import viewsets
from rest_framework.response import Response

from shows.models import Show, Suggestion, LiveVote, PreshowVote
from shows.serializers import (ShowSerializer, SuggestionsSerializer,
                               VoteOptionSerializer, LiveVoteSerializer)
from shows import service as shows_service
from channels import service as channels_service
from users import service as users_service
from utilities.api import APIObject


class ShowAPIObject(APIObject):
    field_list = ['id',
                  'created',
                  'locked',
                  'show_length',
                  'photo_link',
                  'embedded_youtube',
                  'formatted_youtube',
                  'formatted_date',
                  'show_end',
                  'vote_types',
                  'show_seconds_remaining']

    def __init__(self, show, **kwargs):
        super(ShowAPIObject, self).__init__(show, **kwargs)
        self.channel_id = show.channel_id
        self.channel_name = show.channel.name
        current_show = shows_service.get_current_show(self.channel_id)
        # If the Show is the current running show
        if show.id == getattr(current_show, 'id', None):
            # Get the current vote state
            state = channels_service.get_current_vote_state(show.vote_types())
            # Set the current show fields
            self.current_display = state.get('display', 'default')
            self.current_vote_type = state.get('vote_type_id', None)
            # If we're in the voting state
            if self.current_display == 'voting':
                vote_type = channels_service.vote_type_or_404(self.current_vote_type)
                # Get the vote options for this (interval or not)
                self.vote_options = shows_service.fetch_vote_option_ids(
                                                                show_id=show.id,
                                                                vote_type_id=vote_type.id,
                                                                interval=vote_type.current_interval)
            # If we're in the result state
            elif self.current_display == 'result':
                vote_type = channels_service.vote_type_or_404(self.current_vote_type)
                current_voted = shows_service.get_current_voted(show.id,
                                                                vote_type.id,
                                                                vote_type.current_interval)
                # If we haven't established a voted option
                if not current_voted:
                    # Get the vote options for this (interval or not)
                    vote_options = shows_service.fetch_vote_options(show_id=show.id,
                                                                    vote_type_id=vote_type.id,
                                                                    interval=vote_type.current_interval)
                    # Determine the winning option
                    winning_option = shows_service.get_winning_option(vote_type,
                                                                      vote_options,
                                                                      show.id,
                                                                      vote_type.current_interval)
                    # Set the voted winning option
                    shows_service.set_voted_option(show.id,
                                                   vote_type.id,
                                                   vote_type.current_interval,
                                                   suggestion=winning_option.suggestion,
                                                   player=winning_option.player)




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
        self.user_id = getattr(suggestion, 'user_id', None)
        upvote_user_id = kwargs.get('upvote_user_id')
        upvote_session_id = kwargs.get('upvote_session_id')
        if upvote_user_id and upvote_user_id !="None":
            self.user_already_upvoted = bool(PreshowVote.objects.filter(show=suggestion.show_id,
                                                                        suggestion=suggestion,
                                                                        user=upvote_user_id).count())
        elif upvote_session_id and upvote_session_id !="None":
            self.user_already_upvoted = bool(PreshowVote.objects.filter(show=suggestion.show_id,
                                                                        suggestion=suggestion,
                                                                        session_id=upvote_session_id).count())
        else:
            self.user_already_upvoted = False


class VoteOptionAPIObject(APIObject):

    def __init__(self, option, **kwargs):
        super(VoteOptionAPIObject, self).__init__(option, **kwargs)
        self.suggestion_id = option.suggestion_id
        self.used = option.suggestion.used
        self.suggestion = option.suggestion.value
        user_id = option.suggestion.user_id
        if user_id:
            user_profile = users_service.fetch_user_profile(user_id)
            self.user_id = user_profile.user_id
            self.username = user_profile.safe_username


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


class VoteOptionViewSet(viewsets.ViewSet):
    """
    API endpoint that returns leaderboard entries
    """

    def retrieve(self, request, pk=None):
        vote_option = shows_service.fetch_option(pk)
        serializer = VoteOptionSerializer(VoteOptionAPIObject(vote_option))
        return Response(serializer.data)

    def list(self, request):
        pass


class LiveVoteViewSet(viewsets.ViewSet):
    """
    API endpoint that allows live votes to be viewed
    """

    def list(self, request):
        kwargs = {}
        vote_type_id = self.request.query_params.get('vote_type_id')
        interval = self.request.query_params.get('interval')
        suggestion_id = self.request.query_params.get('suggestion_id')
        player_id = self.request.query_params.get('player_id')
        if vote_type_id:
            kwargs['vote_type'] = vote_type_id
        if interval:
            kwargs['interval'] = int(interval)
        if suggestion_id:
            kwargs['suggestion'] = suggestion_id
        if player_id:
            kwargs['player'] = player_id
        count = LiveVote.objects.filter(**kwargs).count()
        serializer = LiveVoteSerializer({'count': count})
        return Response(serializer.data)