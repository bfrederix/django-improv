import datetime
import pytz

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from shows.models import Suggestion, PreshowVote
from shows import service as shows_service
from channels import service as channels_service
from utilities import sessions as session_utils
from utilities import views as view_utils


class ShowControllerView(view_utils.ShowView):
    template_name = 'shows/show_controller.html'

    def get(self, request, *args, **kwargs):
        show_id = kwargs.get('show_id')
        context = self.get_default_channel_context(request, *args, **kwargs)
        context.update({'show_id': int(show_id)})
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        show_id = kwargs.get('show_id')
        vote_start = request.POST.get('vote_start')
        lock_toggle = request.POST.get('lock_toggle')
        context = self.get_default_channel_context(request, *args, **kwargs)
        if vote_start:
            # Get the vote type
            vote_type = channels_service.vote_type_or_404(vote_start)
            # Set the vote type's next interval start
            next_interval = channels_service.start_next_interval(show_id, vote_type)
            # if it's a players only vote type
            if vote_type.players_only:
                suggestions = []
            # Otherwise, fetch a randomized (yet sorted) amount of suggestions
            else:
                suggestions = shows_service.fetch_randomized_suggestions(show_id,
                                                                         vote_type.suggestion_pool_id,
                                                                         vote_type.options)
            # Set the voting options
            shows_service.set_voting_options(context['current_show'],
                                             vote_type,
                                             next_interval,
                                             suggestions=suggestions)
            # Make sure the show is locked
            context['current_show'].locked = True
            context['current_show'].save()
        # If a lock toggle request was made
        elif lock_toggle:
            # If the show is locked, unlock it
            if context['current_show'].locked:
                context['current_show'].locked = False
            # If the show is unlocked, lock it
            else:
                context['current_show'].locked = True
            context['current_show'].save()

        context.update({'show_id': int(show_id)})
        return render(request,
                      self.template_name,
                      context)


class ShowDisplayView(view_utils.ShowView):
    template_name = 'shows/show_display.html'

    def get(self, request, *args, **kwargs):
        show_id = kwargs.get('show_id')
        context = self.get_default_channel_context(request, *args, **kwargs)
        context.update({'show_id': int(show_id)})
        return render(request,
                      self.template_name,
                      context)


class ShowLiveVoteView(view_utils.ShowView):
    template_name = 'shows/show_live_vote.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        return render(request,
                      self.template_name,
                      context)


class ShowSuggestionPoolView(view_utils.ShowView):
    template_name = 'shows/show_suggestion_pool.html'

    def pool_auth_acceptable(self, suggestion_pool, request, context):
        """
        If login is required and the user isn't logged in
        OR if the pool is admin only and the user isn't an admin
        Return False, otherwise return True

        :param suggestion_pool:
        :param request:
        :param context:
        :return bool:
        """
        if suggestion_pool.require_login and not request.user.is_authenticated \
            or suggestion_pool.admin_only and not context['is_channel_admin']:
            return False
        return True

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        session_id = session_utils.get_or_create_session_id(request)
        # Get the Suggestion pool
        suggestion_pool_id = kwargs.get('suggestion_pool_id')
        suggestion_pool = channels_service.suggestion_pool_or_404(suggestion_pool_id)
        # Make sure the user is authenticated properly for the pool
        if not self.pool_auth_acceptable(suggestion_pool, request, context):
            # Redirect the user to the login page
            redirect_url = "{0}?next={1}".format(reverse('user_login'), request.path)
            return HttpResponseRedirect(redirect_url)
        # Determine if the user has reached the max suggestions
        disabled = shows_service.suggestions_maxed(context['current_show'],
                                                   suggestion_pool,
                                                   user_id=getattr(self.request.user, 'id'),
                                                   session_id=session_id)

        context.update({'suggestion_pool': suggestion_pool,
                        'session_id': session_id,
                        'disabled': disabled})
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        action = None
        error = None
        user_id = getattr(self.request.user, 'id')
        delete_id = request.POST.get('delete_id')
        suggestion_value = request.POST.get('suggestion_value')
        context = self.get_default_channel_context(request, *args, **kwargs)
        session_id = session_utils.get_or_create_session_id(request)
        # Get the Suggestion pool
        suggestion_pool_id = kwargs.get('suggestion_pool_id')
        suggestion_pool = channels_service.suggestion_pool_or_404(suggestion_pool_id)
        # Make sure the user is authenticated properly for the pool
        # i.e. require_login or admin_only
        if not self.pool_auth_acceptable(suggestion_pool, request, context):
            # Redirect the user to the login page
            redirect_url = "{0}?next={1}".format(reverse('user_login'), request.path)
            return HttpResponseRedirect(redirect_url)
        # If we are deleting a suggestion
        if delete_id:
            try:
                suggestion = Suggestion.objects.get(pk=delete_id)
            except ObjectDoesNotExist:
                error = "Suggestion already deleted!"
            else:
                # Make sure the user has privileges to delete the suggestion
                # Either they're an admin, or a user matching the user id or session id
                if context['is_channel_admin'] or \
                    suggestion.user_id and suggestion.user_id == user_id or \
                    suggestion.session_id == session_id:
                    # Delete the suggestion
                    suggestion.delete()
        # Add the new suggestion
        elif suggestion_value and not Suggestion.objects.filter(show=context['current_show'],
                                                                value=suggestion_value):
            suggestion_kwargs = {'channel': context['channel'],
                                 'show': context['current_show'],
                                 'suggestion_pool': suggestion_pool,
                                 'used': False,
                                 'voted_on': False,
                                 'amount_voted_on': 0,
                                 'value': suggestion_value,
                                 'preshow_value': 0,
                                 'created': datetime.datetime.utcnow().replace(tzinfo=pytz.utc)}
            if user_id:
                suggestion_kwargs['user'] = request.user
            else:
                suggestion_kwargs['session_id'] = session_id
            Suggestion.objects.get_or_create(**suggestion_kwargs)
        # If the superuser needs to make a bunch of suggestions
        elif request.user and request.user.is_superuser and request.POST.get('suggestalot'):
            suggestion_kwargs = {'channel': context['channel'],
                                 'show': context['current_show'],
                                 'suggestion_pool': suggestion_pool,
                                 'used': False,
                                 'voted_on': False,
                                 'amount_voted_on': 0,
                                 'user': request.user,
                                 'preshow_value': 0,
                                 'created': datetime.datetime.utcnow().replace(tzinfo=pytz.utc)}
            for i in range(1, 51):
                suggestion_kwargs['value'] = "Suggestion-{0}".format(i)
                Suggestion.objects.get_or_create(**suggestion_kwargs)
        elif suggestion_value:
            error = "Suggestion already exists!"
        else:
            error = "Suggestions cannot be blank!"
        # Determine if the user has reached the max suggestions
        disabled = shows_service.suggestions_maxed(context['current_show'],
                                                   suggestion_pool,
                                                   user_id=user_id,
                                                   session_id=session_id)
        # If the user is authenticated, find any suggestion or leaderboard entries with their session id
        # Add their user id to that suggestion/leaderboard entry.
        # Remove the session_id from that suggestion/leaderboard entry.
        context.update({'action': action,
                        'error': error,
                        'suggestion_pool': suggestion_pool,
                        'session_id': session_id,
                        'disabled': disabled})
        return render(request,
                      self.template_name,
                      context)


class UpvoteSubmitView(view_utils.ShowView):

    def post(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        suggestion_id = request.POST.get('id')
        # If a suggestion was submitted properly
        if suggestion_id:
            preshow_kwargs = {'show': context['current_show'],
                              'suggestion': Suggestion.objects.get(pk=suggestion_id),
                              'session_id': session_utils.get_or_create_session_id(request)}
            # If the user is logged in
            if getattr(self.request.user, 'id'):
                preshow_kwargs['user'] = User.objects.get(pk=request.user.id)
            # Get or create the preshow vote
            PreshowVote.objects.get_or_create(**preshow_kwargs)
        return JsonResponse({})