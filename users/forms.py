from django import forms

from utilities.forms import ReadOnlyFieldsMixin, user_agreement_copy


class OptInPreferenceForm(forms.Form):
    site_email_opt_in = forms.BooleanField(required=False)
    user_agreement = forms.CharField(widget=forms.Textarea(), initial=user_agreement_copy)
    user_agreement_opt_in = forms.BooleanField(required=True)


class OptInPreferenceFormReadOnly(OptInPreferenceForm, ReadOnlyFieldsMixin):
    readonly_fields = ('user_agreement',)


class ChangeUsernameForm(forms.Form):
    username = forms.CharField(required=True)
