from django.http import HttpResponseRedirect
from django.http import Http404
from django.core.urlresolvers import reverse

from channels import service as channels_service


def channel_admin_required(function):
    def wrap(request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        channel_name = kwargs.get('channel_name')
        if channel_id:
            channel = channels_service.channel_or_404(channel_id, channel_id=True)
        elif channel_name:
            channel = channels_service.channel_or_404(channel_name)
        else:
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
