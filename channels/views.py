from django.shortcuts import render
from django.views.generic import View

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
