from django.shortcuts import get_object_or_404

from users.models import UserProfile


def update_user_profile(user_id, update_fields):
    user_profile = UserProfile.objects.get(user=user_id)
    for key, value in update_fields.items():
        setattr(user_profile, key, value)
    user_profile.save()
    return user_profile


def fetch_user_profile(user_id):
    if user_id:
        return UserProfile.objects.get(user=user_id)
    else:
        return None


def user_profile_or_404(user_id):
    return get_object_or_404(UserProfile, user_id=user_id)
