from django.shortcuts import redirect

from social.pipeline.partial import partial

from users.models import UserProfile


@partial
def save_opt_in(strategy, details, user=None, is_new=False, *args, **kwargs):
    # Get the request data from the opt-in form
    request_data = kwargs.get('request', {})
    # IF the user is new and the opt-in form hasn't been submitted
    if is_new and not 'ieoi' in request_data:
        return redirect('opt_in_preferences', backend=kwargs['backend'].name)
    elif 'ieoi' in request_data:
        # Get the user profile
        user_profile = UserProfile.objects.get(user=user)
        # Apply the opt in data
        user_profile.improvote_email_opt_in = request_data.get('ieoi', 'False') == 'True'
        user_profile.channels_email_opt_in = request_data.get('ceoi', 'False') == 'True'
        user_profile.save()



def save_user_profile(backend, user, response, *args, **kwargs):
    details = kwargs.get('details')
    if user.email:
        email = user.email
    else:
        email = details.get('email', 'no email')
    update_fields = {'user': user,
                     'social_id': response.get('id'),
                     'login_type': backend.name,
                     'username': email,
                     'first_name': details.get('first_name'),
                     'last_name': details.get('last_name'),
                     'strip_username': email,
                     'email': email}
    # Try to fetch the user profile by their django id
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(**update_fields)
    else:
        # Update the fields we should update everytime they log in
        for field, value in update_fields.items():
            if not field in ['user', 'username', 'strip_username']:
                setattr(user_profile, field, value)
    user_profile.save()