import sys
import os
sys.path.append("/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine")

from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.appengine.api import datastore

from leaderboards.models import Medal, LeaderboardEntry, LeaderboardSpan

for (dirpath, dirnames, filenames) in os.walk('/Users/brandon.fredericks/home_projects/django-voteprov/gae_export/adventureprovbackup/'):
    for filename in filenames:
        if not filename.endswith('backup_info'):
            raw = open(os.path.join(dirpath, filename), 'r')
            reader = records.RecordsReader(raw)
            for record in reader:
                entity_proto = entity_pb.EntityProto(contents=record)
                entity = datastore.Entity.FromPb(entity_proto)
                try:
                    print(entity['show'].id())
                except:
                    pass
