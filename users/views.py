from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.views.generic import View

from users import forms as user_forms


class OptInPreferencesView(View):
    form_class = user_forms.OptInPreferenceForm
    initial = {'improvote_email_opt_in': True,
               'channels_email_opt_in': True}
    template_name = 'opt_in_preferences.html'

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