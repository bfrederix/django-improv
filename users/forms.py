from django import forms

class OptInPreferenceForm(forms.Form):
    improvote_email_opt_in = forms.BooleanField(required=False)
    channels_email_opt_in = forms.BooleanField(required=False)
