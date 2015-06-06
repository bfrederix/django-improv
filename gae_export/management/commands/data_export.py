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

from leaderboards.models import (Medal, LeaderboardEntry, LeaderboardSpan,
                                LeaderboardEntryMedal)
from players.models import Player
from shows.models import (SuggestionPool, VoteType, Show, ShowVoteType,
                          ShowPlayer, ShowPlayerPool, Suggestion,
                          PreshowVote, LiveVote, ShowInterval,
                          VoteOptions, VotedItem)
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
                      ]


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
                                  photo_filename=entity['photo_filename'],
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
                            try:
                                recap_type_id = entity.get('recap_type').id()
                            except AttributeError:
                                recap_type_id = None
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
                                  recap_type_id=recap_type_id,
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
                            if entity['show']:
                                show_id = entity['show'].id()
                            else:
                                show_id = None
                            Suggestion(
                                  id=entity.key().id(),
                                  show_id=show_id,
                                  suggestion_pool_id=entity['suggestion_pool'].id(),
                                  used=entity['used'],
                                  voted_on=entity['voted_on'],
                                  amount_voted_on=entity.get('amount_voted_on'),
                                  value=entity['value'],
                                  preshow_value=entity['preshow_value'],
                                  session_id=entity['session_id'],
                                  user_id=entity['user_id'],
                                  created=entity['created']).save()

        self.stdout.write('Successfully Imported GAE {0}'.format(model_to_import))
