from django.test import TestCase
import os

from benchcoach.utils.teamsnap_sync_engine import TeamsnapSyncEngine

import benchcoach.models

TEAMSNAP_TOKEN = os.environ['TEAMSNAP_TOKEN']
TEAM_TEAMSNAP_ID = os.environ['TEAM_TEAMSNAP_ID']

syncengine = TeamsnapSyncEngine(managed_team_teamsnap_id=TEAM_TEAMSNAP_ID, teamsnap_token=TEAMSNAP_TOKEN)
r=syncengine.import_items('event')
pass

class TestEventModel(TestCase):
    fixtures = ['minimal']

    def setUp(self):
        self.syncengine = TeamsnapSyncEngine(managed_team_teamsnap_id=TEAM_TEAMSNAP_ID, teamsnap_token=TEAMSNAP_TOKEN)

    def test_all_models(self):
        for Model in self.syncengine.models:
            with self.subTest():
                self.syncengine.import_items(Model.__name__.lower())
        pass