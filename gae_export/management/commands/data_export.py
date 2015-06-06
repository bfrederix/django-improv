import sys
import os
import re
from pprint import pprint
sys.path.append("/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine")

from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.appengine.api import datastore

from django.core.management.base import BaseCommand, CommandError

from leaderboards.models import (Medal, LeaderboardEntry, LeaderboardSpan,
                                LeaderboardEntryMedal)
from players.models import Player
from shows.models import (SuggestionPool, VoteType, Show, Suggestion,
                          PreshowVote, LiveVote, ShowInterval,
                          VoteOptions, VotedItem)
from users.models import UserProfile, EmailOptOut


MODEL_NAME_REGEX = '[\w\_]+[\d]{4}\_[\d]{2}\_[\d]{2}\_([\w]+)-'


class Command(BaseCommand):
    help = 'Imports GAE fixtures into the DB'

    def add_arguments(self, parser):
        parser.add_argument('data', nargs='+', type=str)

    def handle(self, *args, **options):
        try:
            data_path = options['data'][0]
            model_to_import = options['data'][1]
        except IndexError:
            raise IndexError("Command requires path argument and model name.")
        appname = "s~deadimprov"
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
                        try:
                            entity['show'].id()
                        except:
                            pass

        self.stdout.write('Successfully Imported GAE {0}'.format(model_to_import))
