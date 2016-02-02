from leaderboards.models import LeaderboardEntry, LeaderboardEntryMedal


def fetch_leaderboard_entries_by_user(user_id):
    return LeaderboardEntry.objects.filter(user=user_id)


def fetch_leaderboard_entries_by_show(show_id, leaderboard_order=False):
    leaderboard_entries = LeaderboardEntry.objects.filter(show=show_id)
    if leaderboard_order:
        return leaderboard_entries.order_by('-wins', '-points')
    return leaderboard_entries


def fetch_medal_ids_by_leaderboard_entry(leaderboard_entry_id):
    return LeaderboardEntryMedal.objects.filter(leaderboard_entry=leaderboard_entry_id).values_list('medal_id', flat=True)