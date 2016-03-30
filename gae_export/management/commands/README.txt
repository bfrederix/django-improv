##### STANDARD NEEDED SQL #######

drop table if exists "auth_group_permissions" cascade;
drop table if exists "auth_group" cascade;
drop table if exists "auth_user_groups" cascade;
drop table if exists "auth_user" cascade;
drop table if exists "auth_user_user_permissions" cascade;
drop table if exists "django_admin_log" cascade;
drop table if exists "django_content_type" cascade;
drop table if exists "auth_permission" cascade;
drop table if exists "django_session" cascade;
drop table if exists "leaderboards_medal" cascade;
drop table if exists "leaderboards_leaderboardentrymedal" cascade;
drop table if exists "leaderboards_leaderboardentry" cascade;
drop table if exists "recaps_showrecap" cascade;
drop table if exists "shows_showvotetype" cascade;
drop table if exists "shows_showplayer" cascade;
drop table if exists "shows_showplayerpool" cascade;
drop table if exists "shows_suggestionpool" cascade;
drop table if exists "shows_preshowvote" cascade;
drop table if exists "shows_livevote" cascade;
drop table if exists "shows_showinterval" cascade;
drop table if exists "shows_voteoptions" cascade;
drop table if exists "shows_optionlist" cascade;
drop table if exists "shows_show" cascade;
drop table if exists "shows_votetype" cascade;
drop table if exists "shows_suggestion" cascade;
drop table if exists "players_player" cascade;
drop table if exists "shows_voteditem" cascade;
drop table if exists "users_userprofile" cascade;
drop table if exists "users_emailoptout" cascade;
drop table if exists "django_migrations" cascade;
drop table if exists "leaderboards_leaderboardspan" cascade;


##### Activating virtualenv (work mac) #########
pyenv activate gae_export


#### Run the management command ############
python manage.py data_export /Users/freddy/projects/django-voteprov/gae_export/adventureprovbackup/ Medal