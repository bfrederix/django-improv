from django.shortcuts import redirect

from social.pipeline.partial import partial

from users.models import UserProfile


@partial
def save_opt_in(strategy, details, user=None, is_new=False, *args, **kwargs):
    #import pdb; pdb.set_trace()
    # Get the request data from the opt-in form
    request_data = kwargs.get('request', {})
    # IF the user is new and the opt-in form hasn't been submitted
    if is_new and not 'ieoi' in request_data:
        return redirect('opt_in_preferences', backend=kwargs['backend'].name)
    elif 'ieoi' in request_data:
        # Get the user profile
        user_profile = UserProfile.objects.get(user_id=user.id)
        # Apply the opt in data
        user_profile.improvote_email_opt_in = request_data.get('ieoi', 'False') == 'True'
        user_profile.channels_email_opt_in = request_data.get('ceoi', 'False') == 'True'
        import pdb; pdb.set_trace()
        user_profile.save()
        return redirect('social:complete', backend=kwargs['backend'].name)


def save_user_profile(backend, user, response, *args, **kwargs):
    # Try to fetch the user profile by their django id
    try:
        user_profile = UserProfile.objects.get(user_id=user.id)
    except UserProfile.DoesNotExist:
        # Create a profile by the django id, social backend, social id
        user_profile =  UserProfile(user_id = user.id,
                                    social_id = response.get('id'),
                                    login_type = backend.name,
                                    username = user.email,
                                    first_name = user.first_name,
                                    last_name = user.last_name,
                                    strip_username = user.email,
                                    email = user.email)
        user_profile.save()