import sys
import os
import re
import datetime
from pprint import pprint
sys.path.append("/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine")

import pytz
from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.appengine.api import datastore

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.models import User

from channels.models import (Channel, ChannelAddress, ChannelAdmin,
                             ChannelOwner, ChannelUser, SuggestionPool, VoteType)
from leaderboards.models import (Medal, LeaderboardEntry, LeaderboardSpan,
                                LeaderboardEntryMedal)
from players.models import Player
from shows.models import (Show, ShowVoteType,
                          ShowPlayer, Suggestion,
                          PreshowVote, LiveVote, ShowInterval,
                          VoteOption, VotedItem)
from users.models import UserProfile


MODEL_NAME_REGEX = '/datastore_backup_datastore_backup_[\d]{4}\_[\d]{2}\_[\d]{2}\_([\w]+)/'

MODEL_IMPORT_ORDER = ['UserProfile',
                      'Medal',
                      'LeaderboardSpan',
                      'Player',
                      'SuggestionPool',
                      'VoteType',
                      'Show',
                      'LeaderboardEntry',
                      'Suggestion',
                      'PreshowVote',
                      'ShowInterval',
                      'VoteOptions',
                      'LiveVote',
                      'VotedItem',
                      'EmailOptOut']

def get_entity_id(entity, entity_name):
    if entity[entity_name]:
        return entity[entity_name].id()
    else:
        return None


class Command(BaseCommand):
    """
    How to run:

    python manage.py data_export [path to exported files] [model name]
    """
    help = 'Imports GAE fixtures into the DB'

    def add_arguments(self, parser):
        parser.add_argument('data', nargs='+', type=str)

    def import_all_fixtures(self, data_path):
        for model in MODEL_IMPORT_ORDER:
            self.import_fixtures(data_path, model)

    def handle(self, *args, **options):
        try:
            data_path = options['data'][0]
        except IndexError:
            raise IndexError("Command requires path argument.")
        except KeyError:
            data_path = args[0]
            try:
                model_to_import = args[1]
            except IndexError:
                self.import_all_fixtures(data_path)
            else:
                self.import_fixtures(data_path, model_to_import)
        else:
            try:
                model_to_import = options['data'][1]
            except IndexError:
                self.import_all_fixtures(data_path)
            else:
                self.import_fixtures(data_path, model_to_import)

    def import_fixtures(self, data_path, model_to_import):
        counter = {'UserProfile': 0,
                   'Medal': 0,
                   'LeaderboardSpan': 0,
                   'Player': 0,
                   'SuggestionPool': 0,
                   'VoteType': 0,
                   'Show': 0,
                   'LeaderboardEntry': 0,
                   'Suggestion': 0,
                   'PreshowVote': 0,
                   'LiveVote': 0,
                   'ShowInterval': 0,
                   'VoteOptions': 0,
                   'VotedItem': 0,
                   'EmailOptOut': 0,
                   'ShowVoteType': 0,
                   'ShowPlayer': 0,
                   'LeaderboardEntryMedal': 0}
        my_user, created = User.objects.get_or_create(username="freddy")
        channel_address, created = ChannelAddress.objects.get_or_create(street="123 Fake St.",
                                                                        city="Denver",
                                                                        state="CO",
                                                                        zipcode="80202")
        try:
            channel = Channel.objects.get(id=1)
        except Channel.DoesNotExist:
            channel, created = Channel.objects.get_or_create(id=1,
                                                             name="adventure",
                                                             display_name="Adventure-prov",
                                                             email="brfredericks@gmail.com",
                                                             premium=True,
                                                             short_description="Adventure-prov rules!",
                                                             description="Adventure-prov rules for real!",
                                                             thumbnail_url="http://www.fake.com",
                                                             team_photo_url="http://www.fake.com",
                                                             website="http://www.fake.com",
                                                             address=channel_address,
                                                             buy_tickets_link="http://www.fake.com",
                                                             next_show=pytz.utc.localize(datetime.datetime(2017, 8, 9)),
                                                             navbar_color="#4596FF",
                                                             background_color="#000000",
                                                             created=pytz.utc.localize(datetime.datetime.utcnow()))
        channel_owner, created = ChannelOwner.objects.get_or_create(channel=channel,
                                                                    user=my_user)
        channel_admin, created = ChannelAdmin.objects.get_or_create(channel=channel,
                                                                    user=my_user)
        now = pytz.utc.localize(datetime.datetime.now())
        for (dirpath, dirnames, filenames) in os.walk(data_path):
            for filename in filenames:
                if filename.startswith('output-'):
                    m = re.search(MODEL_NAME_REGEX, dirpath)
                    model_name = m.group(1)
                    raw = open(os.path.join(dirpath, filename), 'r')
                    reader = records.RecordsReader(raw)
                    for record in reader:
                        entity_proto = entity_pb.EntityProto(contents=record)
                        entity = datastore.Entity.FromPb(entity_proto)
                        if model_name == 'UserProfile' and model_to_import == 'UserProfile':
                            if not UserProfile.objects.filter(social_id=entity['user_id']):
                                if not 'login_type' in entity:
                                    entity['login_type'] = 'google'
                                if not entity['login_type']:
                                    if entity['email'] != 'dkloeck@comcast.net':
                                        entity['login_type'] = 'google'
                                    else:
                                        entity['login_type'] = 'facebook'
                                # Strip the email after @
                                username = entity['username'].split('@')[0]
                                # Truncate the username
                                username = (username[:28] + '..') if len(username) > 30 else username
                                user, created = User.objects.get_or_create(email=entity['email'],
                                                                           username=username)
                                user_profile, created = UserProfile.objects.get_or_create(
                                    user=user,
                                    social_id=entity['user_id'],
                                    username=entity['username'],
                                    strip_username=entity['strip_username'],
                                    email=entity['email'],
                                    login_type=entity['login_type'],
                                    site_email_opt_in=False,
                                    created=pytz.utc.localize(entity['created']))
                                # Adding a user to a channel
                                ChannelUser.objects.get_or_create(channel=channel,
                                                                  user=user,
                                                                  points=0,
                                                                  suggestion_wins=0,
                                                                  show_wins=0,
                                                                  email_opt_in=True)
                                counter['UserProfile'] += 1
                                self.stdout.write(str(counter['UserProfile']))
                        if model_name == 'Medal' and model_to_import == 'Medal':
                            # Change points to winner
                            if entity['name'] == 'points':
                                name = 'winner'
                            else:
                                name = entity['name']
                            try:
                                Medal.objects.get_or_create(
                                      id=entity.key().id(),
                                      name=name,
                                      display_name=entity['display_name'],
                                      description=entity['description'],
                                      image_filename=entity['image_filename'],
                                      icon_filename=entity['icon_filename'])
                            except IntegrityError, e:
                                if not 'duplicate' in str(e):
                                    raise IntegrityError(e)
                                else:
                                    self.stdout.write("Duplicate Medal")
                            else:
                                counter['Medal'] += 1
                                self.stdout.write(str(counter['Medal']))
                        if model_name == 'LeaderboardEntry' and model_to_import == 'LeaderboardEntry':
                            user_profile = UserProfile.objects.get(social_id=entity['user_id'])
                            try:
                                LeaderboardEntry.objects.get_or_create(
                                      id=entity.key().id(),
                                      channel=channel,
                                      show_id=entity['show'].id(),
                                      show_date=pytz.utc.localize(entity['show_date']),
                                      user=user_profile.user,
                                      points=entity['points'],
                                      wins=entity['wins'])
                            except IntegrityError, e:
                                if not 'duplicate' in str(e):
                                    raise IntegrityError(e)
                                else:
                                    self.stdout.write("Duplicate Leaderboard Entry")
                            else:
                                counter['LeaderboardEntry'] += 1
                                self.stdout.write(str(counter['LeaderboardEntry']))
                            if 'medals' in entity:
                                for medal in entity['medals']:
                                    LeaderboardEntryMedal.objects.get_or_create(
                                          leaderboard_entry_id=entity.key().id(),
                                          medal_id=medal.id())
                                    counter['LeaderboardEntryMedal'] += 1
                                    self.stdout.write(str(counter['LeaderboardEntryMedal']))
                        if model_name == 'LeaderboardSpan' and model_to_import == 'LeaderboardSpan':
                            try:
                                LeaderboardSpan.objects.get_or_create(
                                      id=entity.key().id(),
                                      channel=channel,
                                      name=entity['name'],
                                      start_date=entity['start_date'],
                                      end_date=entity['end_date'])
                            except IntegrityError, e:
                                if not 'duplicate' in str(e):
                                    raise IntegrityError(e)
                                else:
                                    self.stdout.write("Duplicate Leaderboard Span")
                            else:
                                counter['LeaderboardSpan'] += 1
                                self.stdout.write(str(counter['LeaderboardSpan']))
                        if model_name == 'Player' and model_to_import == 'Player':
                            try:
                                Player.objects.get_or_create(
                                      id=entity.key().id(),
                                      channel=channel,
                                      name=entity['name'],
                                      photo_url=entity['photo_filename'],
                                      star=entity['star'],
                                      active=True,
                                      archived=False)
                            except IntegrityError, e:
                                if not 'duplicate' in str(e):
                                    raise IntegrityError(e)
                                else:
                                    self.stdout.write("Duplicate Player")
                            else:
                                counter['Player'] += 1
                                self.stdout.write(str(counter['Player']))
                        if model_name == 'SuggestionPool' and model_to_import == 'SuggestionPool':
                            try:
                                SuggestionPool.objects.get_or_create(
                                      id=entity.key().id(),
                                      channel=channel,
                                      name=entity['name'],
                                      display_name=entity['display_name'],
                                      description=entity['description'],
                                      max_user_suggestions=5,
                                      require_login=False,
                                      active=True,
                                      admin_only=False,
                                      archived=False,
                                      created=pytz.utc.localize(entity['created']))
                            except IntegrityError, e:
                                if not 'duplicate' in str(e):
                                    raise IntegrityError(e)
                                else:
                                    self.stdout.write("Duplicate Suggestion Pool")
                            else:
                                counter['SuggestionPool'] += 1
                                self.stdout.write(str(counter['SuggestionPool']))
                        if model_name == 'VoteType' and model_to_import == 'VoteType':
                            if entity.get('created'):
                                sug_created = pytz.utc.localize(entity.get('created'))
                            else:
                                sug_created = now
                            try:
                                VoteType.objects.get_or_create(
                                      id=entity.key().id(),
                                      channel=channel,
                                      name=entity['name'],
                                      display_name=entity['display_name'],
                                      suggestion_pool_id=entity['suggestion_pool'].id(),
                                      preshow_selected=entity['preshow_voted'],
                                      player_options=entity['interval_uses_players'],
                                      players_only=False,
                                      show_player_pool=False,
                                      vote_type_player_pool=False,
                                      eliminate_winning_player=False,
                                      keep_suggestions=False,
                                      require_login=False,
                                      intervals=entity.get('intervals', []),
                                      manual_interval_control=True,
                                      style=entity['style'],
                                      ordering=entity['ordering'],
                                      options=entity['options'],
                                      vote_length=25,
                                      result_length=10,
                                      button_color=entity['button_color'],
                                      active=True,
                                      archived=False,
                                      current_interval=entity['current_interval'],
                                      current_vote_init=pytz.utc.localize(entity['current_init']),
                                      created=sug_created)
                            except IntegrityError, e:
                                if not 'duplicate' in str(e):
                                    raise IntegrityError(e)
                                else:
                                    self.stdout.write("Duplicate Vote Type")
                            else:
                                counter['VoteType'] += 1
                                self.stdout.write(str(counter['VoteType']))
                        if model_name == 'Show' and model_to_import == 'Show':
                            try:
                                Show.objects.get_or_create(
                                      id=entity.key().id(),
                                      channel=channel,
                                      show_length=180,
                                      vote_options=entity['vote_options'],
                                      created=pytz.utc.localize(entity['created']),
                                      current_vote_type_id=entity['current_vote_type'].id(),
                                      locked=entity['locked'],
                                      photo_link=None,
                                      embedded_youtube=None)
                            except IntegrityError, e:
                                if not 'duplicate' in str(e):
                                    raise IntegrityError(e)
                                else:
                                    self.stdout.write("Duplicate Show")
                            else:
                                counter['Show'] += 1
                                self.stdout.write(str(counter['Show']))
                                for vote_type in entity['vote_types']:
                                    if vote_type.id() not in [5453950262181888, 6514223068741632]:
                                        ShowVoteType.objects.get_or_create(
                                              show_id=entity.key().id(),
                                              vote_type_id=vote_type.id())
                                        counter['ShowVoteType'] += 1
                                        self.stdout.write(str(counter['ShowVoteType']))
                                for s_player in entity['players']:
                                    ShowPlayer.objects.get_or_create(
                                          show_id=entity.key().id(),
                                          player_id=s_player.id(),
                                          used=False)
                                    counter['ShowPlayer'] += 1
                                    self.stdout.write(str(counter['ShowPlayer']))
                        if model_name == 'Suggestion' and model_to_import == 'Suggestion':
                            try:
                                user_profile = UserProfile.objects.get(social_id=entity['user_id'])
                                user = user_profile.user
                            except ObjectDoesNotExist:
                                user = None
                            try:
                                Suggestion.objects.get_or_create(
                                      id=entity.key().id(),
                                      channel=channel,
                                      show_id=get_entity_id(entity, 'show'),
                                      suggestion_pool_id=entity['suggestion_pool'].id(),
                                      used=entity['used'],
                                      voted_on=entity['voted_on'],
                                      amount_voted_on=entity.get('amount_voted_on'),
                                      value=entity['value'],
                                      preshow_value=entity['preshow_value'],
                                      session_id=entity['session_id'],
                                      user=user,
                                      created=pytz.utc.localize(entity['created']))
                            except IntegrityError, e:
                                if not 'duplicate' in str(e):
                                    raise IntegrityError(e)
                                else:
                                    self.stdout.write("Duplicate Suggestion")
                            else:
                                counter['Suggestion'] += 1
                                self.stdout.write(str(counter['Suggestion']))
                        if model_name == 'PreshowVote' and model_to_import == 'PreshowVote':
                            try:
                                suggestion = Suggestion.objects.get(id=entity['suggestion'].id())
                            except Suggestion.DoesNotExist:
                                pass
                            else:
                                try:
                                    PreshowVote.objects.get_or_create(
                                          id=entity.key().id(),
                                          show_id=get_entity_id(entity, 'show'),
                                          suggestion_id=entity['suggestion'].id(),
                                          user=None,
                                          session_id=entity['session_id'])
                                except IntegrityError, e:
                                    if not 'not present in table "shows_suggestion"' in str(e) and \
                                       not 'duplicate' in str(e):
                                        raise IntegrityError(e)
                                counter['PreshowVote'] += 1
                                self.stdout.write(str(counter['PreshowVote']))
                        if model_name == 'ShowInterval' and model_to_import == 'ShowInterval':
                            try:
                                show = Show.objects.get(id=entity['show'].id())
                            except Show.DoesNotExist:
                                pass
                            else:
                                try:
                                    vote_type = VoteType.objects.get(id=entity['vote_type'].id())
                                except VoteType.DoesNotExist:
                                    pass
                                else:
                                    try:
                                        show_interval, created = ShowInterval.objects.get_or_create(
                                              show=show,
                                              vote_type=vote_type,
                                              interval=entity['interval'],
                                              player_id=get_entity_id(entity, 'player'))
                                    except IntegrityError, e:
                                        if not 'not present in table "shows_votetype"' in str(e) and \
                                           not 'duplicate' in str(e):
                                            raise IntegrityError(e)
                                    if created:
                                        counter['ShowInterval'] += 1
                                        self.stdout.write(str(counter['ShowInterval']))
                        if model_name == 'VoteOptions' and model_to_import == 'VoteOptions':
                            try:
                                show = Show.objects.get(id=entity['show'].id())
                            except Show.DoesNotExist:
                                pass
                            else:
                                try:
                                    vote_type = VoteType.objects.get(id=entity['vote_type'].id())
                                except VoteType.DoesNotExist:
                                    pass
                                else:
                                    interval = entity['interval']
                                    vote_counter = 0
                                    for option in entity['option_list']:
                                        vote_counter += 1
                                        # Create the vote option
                                        try:
                                            vote_option = VoteOption(
                                                              option_number=vote_counter,
                                                              show=show,
                                                              vote_type=vote_type,
                                                              interval=interval,
                                                              suggestion_id=option.id())
                                            vote_option.save()
                                        except IntegrityError, e:
                                            if not 'not present in table "shows_suggestion"' in str(e) and \
                                               not 'not present in table "shows_voteoptions"' in str(e) and \
                                               not 'duplicate' in str(e):
                                                raise IntegrityError(e)
                                        counter['VoteOptions'] += 1
                                        self.stdout.write(str(counter['VoteOptions']))
                        if model_name == 'LiveVote' and model_to_import == 'LiveVote':
                            try:
                                show = Show.objects.get(id=entity['show'].id())
                            except Show.DoesNotExist:
                                pass
                            else:
                                try:
                                    vote_type = VoteType.objects.get(id=entity['vote_type'].id())
                                except VoteType.DoesNotExist:
                                    pass
                                else:
                                    try:
                                        user_profile = UserProfile.objects.get(social_id=entity['user_id'])
                                        user = user_profile.user
                                    except ObjectDoesNotExist:
                                        user = None
                                    suggestion_id = get_entity_id(entity, 'suggestion')
                                    # If this was a vote with suggestions attached to the live vote
                                    if suggestion_id:
                                        try:
                                            suggestion = Suggestion.objects.get(id=suggestion_id)
                                        except Suggestion.DoesNotExist:
                                            pass
                                        else:
                                            try:
                                                # Get the vote option for the live vote
                                                vote_option = VoteOption.objects.get(
                                                                       show=show,
                                                                       vote_type=vote_type,
                                                                       interval=entity['interval'],
                                                                       suggestion=suggestion)
                                            except ObjectDoesNotExist:
                                                self.stdout.write("Missing Vote Option for LiveVote: {0}".format(entity.key().id()))
                                            except MultipleObjectsReturned:
                                                self.stdout.write("Multiple Vote Options for LiveVote: {0}".format(entity.key().id()))
                                            else:
                                                # Get the show interval for the live vote
                                                try:
                                                    show_interval = ShowInterval.objects.get(
                                                                           show=show,
                                                                           vote_type=vote_type,
                                                                           interval=entity['interval'])
                                                except ObjectDoesNotExist:
                                                    self.stdout.write("Missing Show Interval for Live Vote: {0}".format(entity.key().id()))
                                                else:
                                                    try:
                                                        lv, created = LiveVote.objects.get_or_create(
                                                                          vote_option=vote_option,
                                                                          show_interval=show_interval,
                                                                          session_id=entity['session_id'],
                                                                          user=user)
                                                    except IntegrityError, e:
                                                        if not 'not present in table "shows_votetype"' in str(e) and \
                                                           not 'not present in table "shows_suggestion"' in str(e) and \
                                                           not 'duplicate' in str(e):
                                                            raise IntegrityError(e)
                                                    if created:
                                                        counter['LiveVote'] += 1
                                                        self.stdout.write(str(counter['LiveVote']))
                                    # This was a player live vote and we don't care about recording the live votes
                                    else:
                                        self.stdout.write("Player Live Vote (Don't Care): {0}".format(entity.key().id()))
                        if model_name == 'VotedItem' and model_to_import == 'VotedItem':
                            try:
                                show = Show.objects.get(id=entity['show'].id())
                            except Show.DoesNotExist:
                                pass
                            else:
                                try:
                                    vote_type = VoteType.objects.get(id=entity['vote_type'].id())
                                except VoteType.DoesNotExist:
                                    pass
                                else:
                                    suggestion_id = get_entity_id(entity, 'suggestion')
                                    # If it was a suggestion that was voted for
                                    if suggestion_id:
                                        # Get the vote option for the live vote
                                        try:
                                            vote_option = VoteOption.objects.get(
                                                                   show=show,
                                                                   vote_type=vote_type,
                                                                   interval=entity['interval'],
                                                                   suggestion=suggestion_id)
                                        except ObjectDoesNotExist:
                                            self.stdout.write("Missing Vote Option for VotedItem: {0}".format(entity.key().id()))
                                        except MultipleObjectsReturned:
                                            self.stdout.write("Multiple Vote Options for VotedItem: {0}".format(entity.key().id()))
                                        else:
                                            try:
                                                VotedItem.objects.get_or_create(
                                                          show=show,
                                                          vote_type=vote_type,
                                                          vote_option=vote_option,
                                                          interval=entity['interval'])
                                            except IntegrityError, e:
                                                if not 'not present in table "shows_votetype"' in str(e) and \
                                                   not 'not present in table "shows_suggestion"' in str(e) and \
                                                   not 'duplicate' in str(e):
                                                    raise IntegrityError(e)
                                            counter['VotedItem'] += 1
                                            self.stdout.write(str(counter['VotedItem']))
                                    # This was a player voted item and we don't care about recording the live votes
                                    else:
                                        self.stdout.write("Player Voted Item (Don't Care): {0}".format(entity.key().id()))
                        if model_name == 'EmailOptOut' and model_to_import == 'EmailOptOut':
                            try:
                                up = UserProfile.objects.get(email=entity['email'])
                            except ObjectDoesNotExist:
                                pass
                            else:
                                cu = ChannelUser.objects.get(channel=channel,
                                                             user=up.user)
                                cu.email_opt_in = False
                                cu.save()
                            counter['EmailOptOut'] += 1
                            self.stdout.write(str(counter['EmailOptOut']))


        self.stdout.write('Successfully Imported GAE {0}'.format(model_to_import))
