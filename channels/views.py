from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from channels import service as channels_service
from users import service as users_service


class ChannelHomeView(View):
    template_name = 'channels/channel_home.html'

    def get(self, request, *args, **kwargs):
        channel_name = kwargs.get('channel_name')
        channel = channels_service.channel_or_404(channel_name)
        is_channel_admin = channels_service.check_is_channel_admin(channel,
                                                                   getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        return render(request,
                      self.template_name,
                      {'channel': channel,
                       'user_profile': user_profile,
                       'is_channel_admin': is_channel_admin})

@csrf_exempt
def channel_user_update(request, *args, **kwargs):
    channel_name = kwargs.get('channel_name')
    user_id = kwargs.get('user_id')
    channel = channels_service.channel_or_404(channel_name)
    if request.method == 'POST' and user_id:
        channels_service.update_channel_user(channel.id, user_id)
        return HttpResponse("Channel User Updated", content_type='text/plain')
    return HttpResponse("Not Updated", content_type='text/plain')