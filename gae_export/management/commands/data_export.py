import sys
import os
import re
import datetime
from pprint import pprint
sys.path.append("/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine")

from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.appengine.api import datastore

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from leaderboards.models import (Medal, LeaderboardEntry, LeaderboardSpan,
                                LeaderboardEntryMedal)
from players.models import Player
from shows.models import (SuggestionPool, VoteType, Show, ShowVoteType,
                          ShowPlayer, ShowPlayerPool, Suggestion,
                          PreshowVote, LiveVote, ShowInterval,
                          VoteOptions, OptionList, VotedItem)
from users.models import UserProfile, EmailOptOut


MODEL_NAME_REGEX = '[\w\_]+[\d]{4}\_[\d]{2}\_[\d]{2}\_([\w]+)-'

MODEL_IMPORT_ORDER = ['Medal',
                      'LeaderboardSpan',
                      'Player',
                      'SuggestionPool',
                      'VoteType',
                      'Show',
                      'LeaderboardEntry',
                      'Suggestion',
                      'PreshowVote',
                      'LiveVote',
                      'ShowInterval',
                      'VoteOptions',
                      'VotedItem',
                      'UserProfile',
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

    def handle(self, *args, **options):
        try:
            data_path = options['data'][0]
        except IndexError:
            raise IndexError("Command requires path argument.")

        try:
            model_to_import = options['data'][1]
        except IndexError:
            for model in MODEL_IMPORT_ORDER:
                self.import_fixtures(data_path, model)
        else:
            self.import_fixtures(data_path, model_to_import)

    def import_fixtures(self, data_path, model_to_import):
        now = datetime.datetime.now()
        for (dirpath, dirnames, filenames) in os.walk(data_path):
            for filename in filenames:
                if not filename.endswith('backup_info'):
                    m = re.search(MODEL_NAME_REGEX, filename)
                    model_name = m.group(1)
                    raw = open(os.path.join(dirpath, filename), 'r')
                    reader = records.RecordsReader(raw)
                    for record in reader:
                        entity_proto = entity_pb.EntityProto(contents=record)
                        entity = datastore.Entity.FromPb(entity_proto)
                        if model_name == 'Medal' and model_to_import == 'Medal':
                            Medal(id=entity.key().id(),
                                  name=entity['name'],
                                  display_name=entity['display_name'],
                                  description=entity['description'],
                                  image_filename=entity['image_filename'],
                                  icon_filename=entity['icon_filename']).save()
                        if model_name == 'LeaderboardEntry' and model_to_import == 'LeaderboardEntry':
                            LeaderboardEntry(
                                  id=entity.key().id(),
                                  show_id=entity['show'].id(),
                                  show_date=entity['show_date'],
                                  user_id=entity['user_id'],
                                  points=entity['points'],
                                  wins=entity['wins']).save()
                            LeaderboardEntryMedal(
                                  leaderboard_entry_id=entity.key().id(),
                                  medal_id=entity['medal'].id()).save()
                        if model_name == 'LeaderboardSpan' and model_to_import == 'LeaderboardSpan':
                            LeaderboardSpan(
                                  id=entity.key().id(),
                                  name=entity['name'],
                                  start_date=entity['start_date'],
                                  end_date=entity['end_date']).save()
                        if model_name == 'Player' and model_to_import == 'Player':
                            Player(
                                  id=entity.key().id(),
                                  name=entity['name'],
                                  photo_url=entity['photo_filename'],
                                  star=entity['star']).save()
                        if model_name == 'SuggestionPool' and model_to_import == 'SuggestionPool':
                            SuggestionPool(
                                  id=entity.key().id(),
                                  name=entity['name'],
                                  display_name=entity['display_name'],
                                  description=entity['description'],
                                  created=entity['created']).save()
                        if model_name == 'VoteType' and model_to_import == 'VoteType':
                            #pprint(entity['intervals'])
                            VoteType(
                                  id=entity.key().id(),
                                  name=entity['name'],
                                  display_name=entity['display_name'],
                                  suggestion_pool_id=entity['suggestion_pool'].id(),
                                  preshow_voted=entity['preshow_voted'],
                                  has_intervals=entity['has_intervals'],
                                  interval_uses_players=entity['interval_uses_players'],
                                  intervals=entity.get('intervals', []),
                                  style=entity['style'],
                                  occurs=entity['occurs'],
                                  ordering=entity['ordering'],
                                  options=entity['options'],
                                  randomize_amount=entity['randomize_amount'],
                                  button_color=entity['button_color'],
                                  current_interval=entity['current_interval'],
                                  current_init=entity['current_init'],
                                  created=entity.get('created') or now).save()
                        if model_name == 'Show' and model_to_import == 'Show':
                            Show(
                                  id=entity.key().id(),
                                  vote_length=entity['vote_length'],
                                  result_length=entity['result_length'],
                                  vote_options=entity['vote_options'],
                                  timezone=entity['timezone'],
                                  created=entity['created'],
                                  archived=entity['archived'],
                                  current_vote_type_id=entity['current_vote_type'].id(),
                                  current_vote_init=entity['current_vote_init'],
                                  recap_type_id=get_entity_id(entity, 'recap_type'),
                                  recap_init=entity['recap_init'],
                                  locked=entity['locked']).save()
                            for vote_type in entity['vote_types']:
                                if vote_type.id() not in [5453950262181888, 6514223068741632]:
                                    ShowVoteType(
                                          show_id=entity.key().id(),
                                          vote_type_id=vote_type.id()).save()
                            for s_player in entity['players']:
                                ShowPlayer(
                                      show_id=entity.key().id(),
                                      player_id=s_player.id()).save()
                            for p_player in entity['player_pool']:
                                ShowPlayerPool(
                                      show_id=entity.key().id(),
                                      player_id=p_player.id()).save()
                        if model_name == 'Suggestion' and model_to_import == 'Suggestion':
                            Suggestion(
                                  id=entity.key().id(),
                                  show_id=get_entity_id(entity, 'show'),
                                  suggestion_pool_id=entity['suggestion_pool'].id(),
                                  used=entity['used'],
                                  voted_on=entity['voted_on'],
                                  amount_voted_on=entity.get('amount_voted_on'),
                                  value=entity['value'],
                                  preshow_value=entity['preshow_value'],
                                  session_id=entity['session_id'],
                                  user_id=entity['user_id'],
                                  created=entity['created']).save()
                        if model_name == 'PreshowVote' and model_to_import == 'PreshowVote':
                            try:
                                PreshowVote(
                                      id=entity.key().id(),
                                      show_id=get_entity_id(entity, 'show'),
                                      suggestion_id=entity['suggestion'].id(),
                                      session_id=entity['session_id']).save()
                            except IntegrityError, e:
                                if not 'not present in table "shows_suggestion"' in str(e):
                                    raise IntegrityError(e)
                        if model_name == 'LiveVote' and model_to_import == 'LiveVote':
                            try:
                                LiveVote(
                                      id=entity.key().id(),
                                      show_id=entity['show'].id(),
                                      vote_type_id=entity['vote_type'].id(),
                                      player_id=get_entity_id(entity, 'player'),
                                      suggestion_id=get_entity_id(entity, 'suggestion'),
                                      interval=entity['interval'],
                                      session_id=entity['session_id'],
                                      user_id=entity['user_id']).save()
                            except IntegrityError, e:
                                if not 'not present in table "shows_votetype"' in str(e) and \
                                   not 'not present in table "shows_suggestion"' in str(e):
                                    raise IntegrityError(e)
                        if model_name == 'ShowInterval' and model_to_import == 'ShowInterval':
                            try:
                                ShowInterval(
                                      id=entity.key().id(),
                                      show_id=entity['show'].id(),
                                      vote_type_id=entity['vote_type'].id(),
                                      interval=entity['interval'],
                                      player_id=get_entity_id(entity, 'player')).save()
                            except IntegrityError, e:
                                if not 'not present in table "shows_votetype"' in str(e):
                                    raise IntegrityError(e)
                        if model_name == 'VoteOptions' and model_to_import == 'VoteOptions':
                            try:
                                VoteOptions(
                                      id=entity.key().id(),
                                      show_id=entity['show'].id(),
                                      vote_type_id=entity['vote_type'].id(),
                                      interval=entity['interval']).save()
                            except IntegrityError, e:
                                if not 'not present in table "shows_votetype"' in str(e):
                                    raise IntegrityError(e)
                            for option in entity['option_list']:
                                try:
                                    OptionList(
                                          vote_option_id=entity.key().id(),
                                          suggestion_id=option.id()).save()
                                except IntegrityError, e:
                                    if not 'not present in table "shows_suggestion"' in str(e) and \
                                       not 'not present in table "shows_voteoptions"' in str(e):
                                        raise IntegrityError(e)
                        if model_name == 'VotedItem' and model_to_import == 'VotedItem':
                            try:
                                VotedItem(
                                          id=entity.key().id(),
                                          show_id=entity['show'].id(),
                                          vote_type_id=entity['vote_type'].id(),
                                          player_id=get_entity_id(entity, 'player'),
                                          suggestion_id=get_entity_id(entity, 'suggestion'),
                                          interval=entity['interval']).save()
                            except IntegrityError, e:
                                if not 'not present in table "shows_votetype"' in str(e) and \
                                   not 'not present in table "shows_suggestion"' in str(e):
                                    raise IntegrityError(e)
                        if model_name == 'UserProfile' and model_to_import == 'UserProfile':
                            if not UserProfile.objects.filter(user_id=entity['user_id']):
                                if not 'login_type' in entity:
                                    entity['login_type'] = 'google'
                                if not entity['login_type']:
                                    if entity['email'] != 'dkloeck@comcast.net':
                                        entity['login_type'] = 'google'
                                    else:
                                        entity['login_type'] = 'facebook'
                                UserProfile(
                                    id=entity.key().id(),
                                    user_id=entity['user_id'],
                                    username=entity['username'],
                                    strip_username=entity['strip_username'],
                                    email=entity['email'],
                                    login_type=entity['login_type'],
                                    current_session=entity['current_session'],
                                    fb_access_token=entity.get('fb_access_token'),
                                    created=entity['created']).save()
                        if model_name == 'EmailOptOut' and model_to_import == 'EmailOptOut':
                                EmailOptOut(
                                    id=entity.key().id(),
                                    email=entity['email']).save()

        self.stdout.write('Successfully Imported GAE {0}'.format(model_to_import))
