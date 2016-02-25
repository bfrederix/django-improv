import datetime
import random
import pytz

from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
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
        user_profile.site_email_opt_in = request_data.get('ieoi', 'False') == 'True'
        user_profile.channels_email_opt_in = request_data.get('ceoi', 'False') == 'True'
        user_profile.save()



def save_user_profile(backend, user, response, *args, **kwargs):
    details = kwargs.get('details')
    # Get the e-mail from the response
    if user.email:
        email = user.email
    else:
        email = details.get('email', 'no email')

    # These are the basic fields we'll be updating every time a user logs in
    update_fields = {'social_id': response.get('id'),
                     'login_type': backend.name,
                     'first_name': details.get('first_name'),
                     'last_name': details.get('last_name'),
                     'email': email,
                     'created': datetime.datetime.utcnow().replace(tzinfo=pytz.utc)}
    # See if the user profile exists
    try:
        user_profile = UserProfile.objects.get(user=user)
    # IF the user profile doesn't exist, create a new username if needed
    except UserProfile.DoesNotExist:
        try:
            # Get the username
            username = email.split('@')[0]
        except IndexError:
            # If we couldn't pull a proper username, generate one
            username = "user{0}".format(str(random.getrandbits(20)))
        # Get the stripped and lowercase username
        strip_username = username.strip().lower()
        # Make sure the username is unique
        try:
            UserProfile.objects.get(strip_username=strip_username)
        except ObjectDoesNotExist:
            pass
        else:
            # Add random numbers to the end of their username
            random_string = str(random.getrandbits(20))
            username = "{0}{1}".format(username, random_string)
            strip_username = "{0}{1}".format(strip_username, random_string)

        # Update the username for the User and save it
        user.username = username
        user.save()
        # Add the fields for the user profile creation
        update_fields.update(
            {'user': user,
             'username': username,
             'strip_username': strip_username}
        )
        # Create the user profile
        user_profile = UserProfile(**update_fields)
    # The user profile already existed
    else:
        # Update the fields we should update every time they log in
        for field, value in update_fields.items():
            setattr(user_profile, field, value)
    # Save/Create the user profile
    user_profile.save()