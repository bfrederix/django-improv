from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.views.generic import View

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
