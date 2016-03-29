from django import forms

from utilities.forms import ReadOnlyFieldsMixin, user_agreement_copy


class OptInPreferenceForm(forms.Form):
    user_agreement = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 50}),
                                     initial=user_agreement_copy)
    user_agreement_opt_in = forms.BooleanField(required=True)

class OptInPreferenceFormReadOnly(OptInPreferenceForm, ReadOnlyFieldsMixin):
    readonly_fields = ('user_agreement',)


class ChangeUsernameForm(forms.Form):
    username = forms.CharField(required=True)
