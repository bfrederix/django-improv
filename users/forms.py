from django import forms


class OptInPreferenceForm(forms.Form):
    site_email_opt_in = forms.BooleanField(required=False)


class ChangeUsernameForm(forms.Form):
    username = forms.CharField(required=True)