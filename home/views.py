from django.shortcuts import render
from django.views.generic import View

from users import service as users_service


class HomeView(View):
    template_name = 'home/home.html'

    def get(self, request, *args, **kwargs):
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))

        return render(request,
                      self.template_name,
                      {'user_profile': user_profile})