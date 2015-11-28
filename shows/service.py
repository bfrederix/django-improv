from shows.models import Suggestion


def fetch_suggestion_count_by_user(user_id):
    if user_id:
        return Suggestion.objects.filter(user=user_id).count()
    else:
        return 0