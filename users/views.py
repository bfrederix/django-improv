from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.views.generic import View

from users import forms as user_forms
from channels import service as channels_service
from users import service as users_service


class OptInPreferencesView(View):
    form_class = user_forms.OptInPreferenceForm
    initial = {'improvote_email_opt_in': True,
               'channels_email_opt_in': True}
    template_name = 'embedded_utils/opt_in_preferences.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name,
                      {'form': form,
                       'backend': kwargs.get('backend')})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            ieoi = form.cleaned_data.get('improvote_email_opt_in', False)
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
    form_class = user_forms.ChangeUsernameForm
    second_form_class = user_forms.OptInPreferenceForm
    template_name = 'users/user_account.html'

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        channel_name = request.GET.get('channel_name')
        if channel_name:
            channel = channels_service.channel_or_404(channel_name)
        else:
            channel = None
        form = self.form_class()
        form2 = self.second_form_class()
        user_profile = users_service.fetch_user_profile(user_id)
        return render(request,
                      self.template_name,
                      {'user_account_page': True,
                       'form': form,
                       'form2': form2,
                       'page_user_profile': user_profile,
                       'channel': channel})

    def form_invalid(self, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        if 'form' in request.POST:
            form_class = self.get_form_class()
            form_name = 'form'
        else:
            form_class = self.second_form_class
            form_name = 'form2'

        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(**{form_name: form})
