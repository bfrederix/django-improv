from django.shortcuts import get_object_or_404

from shows.models import Show, Suggestion


def show_or_404(show_id):
    return get_object_or_404(Show, pk=show_id)


def fetch_suggestion_count_by_user(user_id, show_id=None):
    if user_id:
        kwargs = {'user': user_id}
        if show_id:
            kwargs['show'] = show_id
        return Suggestion.objects.filter(**kwargs).count()
    else:
        return 0


def suggestion_or_404(suggestion_id):
    return get_object_or_404(Suggestion, pk=suggestion_id)