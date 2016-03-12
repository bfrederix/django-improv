from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from users.models import UserProfile


def update_user_profile(user_id, update_fields):
    user_profile = UserProfile.objects.get(user=user_id)
    for key, value in update_fields.items():
        setattr(user_profile, key, value)
    user_profile.save()
    return user_profile


def fetch_user_profile(user_id=None, username=None):
    if user_id:
        return UserProfile.objects.get(user=user_id)
    elif username:
        return UserProfile.objects.get(username=username)
    else:
        return None


def user_update(user_profile, user_id, stripped_username, username):
    # Fetch the django user
    user = User.objects.get(pk=user_id)
    # Change the username and save it
    user.username = username
    user.save()

    # Change the stripped username and username of the user profile and save it
    user_profile.strip_username = stripped_username
    user_profile.username = username
    user_profile.save()


def update_username(user_id, username):
    # Get the stripped, lowercase version of the new username
    stripped_username = username.replace(" ", "").lower()
    try:
        up = UserProfile.objects.get(strip_username=stripped_username)
    except UserProfile.DoesNotExist:
        # Get the user profile by id
        up = UserProfile.objects.get(user=user_id)
        # Update the user and user profile
        user_update(up, user_id, stripped_username, username)
    else:
        # If the users match
        if up.user_id == user_id:
            # It's fine to update it because it's the same user
            user_update(up, user_id, stripped_username, username)
        # The username is already taken
        else:
            return "Username already taken."

def user_profile_or_404(user_id):
    return get_object_or_404(UserProfile, user_id=user_id)
