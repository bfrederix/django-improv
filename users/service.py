from users.models import UserProfile


def update_user_profile(user_id, update_fields):
    user_profile = UserProfile.objects.get(user=user_id)
    for key, value in update_fields.items():
        setattr(user_profile, key, value)
    user_profile.save()
    return user_profile