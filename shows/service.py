import re

from django.shortcuts import get_object_or_404

from shows.models import (Show, Suggestion, VotedItem,
                          VoteOptions, OptionSuggestion)


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


def fetch_voted_items_by_show(show_id, ordered=False):
    voted_items = VotedItem.objects.filter(show=show_id)
    if ordered:
        voted_items = voted_items.order_by('vote_type__ordering', 'interval')
    return voted_items


def fetch_vote_options(show=None, vote_type=None, interval=None):
    kwargs = {}
    if show:
       kwargs['show'] = show
    if vote_type:
       kwargs['vote_type'] = vote_type
    if interval is not None:
       kwargs['interval'] = interval
    return VoteOptions.objects.filter(**kwargs)


def fetch_option_suggestion(vote_option_id):
    return OptionSuggestion.objects.filter(vote_option=vote_option_id)


def create_show(channel_id, players, vote_types):
    pass


def validate_youtube(url):
    youtube_regex = (r'(https?://)?(www\.)?' '(youtube|youtu|youtube-nocookie)\.(com|be)/' '(watch\?.*?(?=v=)v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)

    return youtube_regex_match