from django.shortcuts import render
from django.views.generic import View

from users import service as users_service
from channels import service as channels_service


class HomeView(View):
    template_name = 'home/home.html'

    def get(self, request, *args, **kwargs):
        admin_channels = None
        user_channels = None
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        if user_profile:
            admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
            # If they aren't an admin of a channel
            if not admin_channels:
                user_channels = channels_service.get_channels_by_user(
                                            getattr(self.request.user, 'id'))

        return render(request,
                      self.template_name,
                      {'user_profile': user_profile,
                       'admin_channels': admin_channels,
                       'user_channels': user_channels,
                       'home': True})