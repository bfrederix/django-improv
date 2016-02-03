from django.http import HttpResponse
from django.views.generic import View

from channels import service as channels_service
from shows import service as shows_service


class ShowView(View):

    def get_default_channel_context(self, request, *args, **kwargs):
        context = {}
        # Get the channel ids from the kwargs
        channel_name = kwargs.get('channel_name')
        channel_id = kwargs.get('channel_id')
        # If a channel name was given
        if channel_name:
            context['channel'] = channels_service.channel_or_404(channel_name)
        # If a channel id was given
        elif channel_id:
            context['channel'] = channels_service.channel_or_404(channel_id,
                                                                 channel_id=True)
        # If no channel was found
        else:
            context['channel'] = None
        # If a channel was found, see if the user is an admin
        if context['channel']:
            context['is_channel_admin'] = channels_service.check_is_channel_admin(
                                                context['channel'],
                                                getattr(self.request.user, 'id'))
        # Get the channels that the user is an admin of
        context['admin_channels'] = channels_service.get_channels_by_admin(
                                            getattr(self.request.user, 'id'))
        # Determine if there is a current show for this channel
        context['current_show'] = shows_service.get_current_show(context['channel'].id)
        if context['current_show']:
            # Get the vote types by a list of ids
            vote_types = channels_service.fetch_vote_types_by_ids(
                                                context['current_show'].vote_types())
            # Get the suggestion pools for the current show if it exists
            context['suggestion_pools'] = shows_service.get_vote_types_suggestion_pools(
                                                vote_types)
        return context


def robots_txt(request):
    robots_txt = """User-agent: *
Disallow: /"""

    live_txt = """User-agent: *
Allow: /$
Allow: /leaderboards
Allow: /recap
Allow: /user
Allow: /medals
Disallow: /"""
    return HttpResponse(robots_txt, content_type='text/plain')

def loader_io(request):
    robots_txt = "loaderio-9b6fa50492da1609dc61b9198b767688"
    return HttpResponse(robots_txt, content_type='text/plain')