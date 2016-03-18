from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse, RegexURLResolver
from django.conf.urls import url

from channels import service as channels_service


def channel_admin_required(function):
    def wrap(request, *args, **kwargs):
        # Get the channel id from the path kwargs
        channel_id = kwargs.get('channel_id')
        channel_name = kwargs.get('channel_name')
        if channel_id:
            channel = channels_service.channel_or_404(channel_id, channel_id=True)
        elif channel_name:
            channel = channels_service.channel_or_404(channel_name)
        else:
            # Get the channel from the GET parameters or the session
            channel = channels_service.channel_from_request(request)
            # If no channel was found
            if not channel:
                raise Http404

        is_channel_admin = channels_service.check_is_channel_admin(channel,
                                                                   getattr(request.user, 'id'))
        if is_channel_admin:
             return function(request, *args, **kwargs)
        else:
            redirect_url = "{0}?next={1}".format(reverse('user_login'), request.path)
            return HttpResponseRedirect(redirect_url)

    wrap.__doc__=function.__doc__
    wrap.__name__=function.__name__
    return wrap


def channel_owner_required(function):
    def wrap(request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        channel_name = kwargs.get('channel_name')
        if channel_id:
            channel = channels_service.channel_or_404(channel_id, channel_id=True)
        elif channel_name:
            channel = channels_service.channel_or_404(channel_name)
        else:
            raise Http404

        is_channel_owner = channels_service.check_is_channel_owner(channel,
                                                                   getattr(request.user, 'id'))
        if is_channel_owner:
             return function(request, *args, **kwargs)
        else:
            redirect_url = "{0}?next={1}".format(reverse('user_login'), request.path)
            return HttpResponseRedirect(redirect_url)

    wrap.__doc__=function.__doc__
    wrap.__name__=function.__name__
    return wrap


def decorate_url(decorator, urlconf):
    '''Recreates the url object with the callback decorated'''
    # urlconf autoresolves names, so callback will always be a function
    return url(urlconf._regex, decorator(urlconf.callback), urlconf.default_args, urlconf.name)

def decorate_include(decorator, urlpatterns):
    urls = [
        decorate_url(decorator, urlconf) if not isinstance(urlconf, RegexURLResolver) else decorate_include(decorator, urlconf)
        for urlconf in urlpatterns[0].urlpatterns
    ]
    return (urls,) + urlpatterns[1:]