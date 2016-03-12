import re

from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.utils.html import escape

from users import forms as user_forms
from channels import service as channels_service
from users import service as users_service


class UserLoginView(View):
    template_name = 'users/user_login.html'

    def get(self, request, *args, **kwargs):
        next = request.GET.get('next')
        return render(request,
                      self.template_name,
                      {'next': next})


class OptInPreferencesView(View):
    form_class = user_forms.OptInPreferenceForm
    initial = {'site_email_opt_in': False,
               'channels_email_opt_in': True}
    template_name = 'users/opt_in_preferences.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name,
                      {'form': form,
                       'backend': kwargs.get('backend')})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            ieoi = form.cleaned_data.get('site_email_opt_in', False)
            ceoi = form.cleaned_data.get('channels_email_opt_in', False)
            #user_service.update_user_profile(request.user.id, update_fields)
            # Use cleaned data to update the user preferences
            return redirect("{0}?ieoi={1}&ceoi={2}".format(
                                reverse('social:complete', kwargs={"backend": kwargs.get('backend')}),
                                ieoi,
                                ceoi))
        return render(request, self.template_name,
                      {'form': form,
                       'backend': kwargs.get('backend')})


class UserAccountView(View):
    template_name = 'users/user_account.html'

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        channel_name = request.GET.get('channel_name')
        if channel_name:
            channel = channels_service.channel_or_404(channel_name)
        else:
            channel = None
        user_profile = users_service.fetch_user_profile(user_id)
        return render(request,
                      self.template_name,
                      {'user_account_page': True,
                       'page_user_profile': user_profile,
                       'channel': channel})

    def post(self, request, *args, **kwargs):
        action = None
        error = None
        user_id = int(kwargs.get('user_id'))
        new_username = escape(request.POST.get('username-input', ''))
        channel_name = request.POST.get('channel_name')
        if channel_name:
            channel = channels_service.channel_or_404(channel_name)
        else:
            channel = None
        user_profile = users_service.fetch_user_profile(user_id)
        # Make sure a new username was supplied
        if not new_username:
            error = "Username cannot be empty."
        # Make sure the username is valid
        elif not re.match(r"[\w\- ]+", new_username):
            error = "Username must be a combination of letters, numbers, hyphens, or underscores."
        # Make sure they are the correct user or a superuser
        elif getattr(request.user, 'id') == user_id or getattr(request.user, 'is_superuser'):
            action = 'Changed Username Successfully!'
            error = users_service.update_username(user_id,
                                                  new_username)
        # This isn't the same user as the person viewing the page
        else:
            error = "You don't have permission to change this username."

        return render(request,
                      self.template_name,
                      {'user_account_page': True,
                       'page_user_profile': user_profile,
                       'channel': channel,
                       'action': action,
                       'error': error})
