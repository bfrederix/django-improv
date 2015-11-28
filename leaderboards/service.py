from leaderboards.models import LeaderboardEntry, LeaderboardEntryMedal


def fetch_leaderboard_entries_by_user(user_id):
    return LeaderboardEntry.objects.filter(user=user_id)


def fetch_medals_by_leaderboard_entry(leaderboard_entry_id):
    return LeaderboardEntryMedal.objects.filter(leaderboard_entry=leaderboard_entry_id)