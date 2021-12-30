from django.test import TestCase
import os

from teamsnap.utils.teamsnap_sync_engine import TeamsnapSyncEngine

import benchcoach.models
import teamsnap.models

TEAMSNAP_TOKEN = os.environ['TEAMSNAP_TOKEN']
TEAM_TEAMSNAP_ID = os.environ['TEAM_TEAMSNAP_ID']

pass

# syncengine = TeamsnapSyncEngine(managed_team_teamsnap_id=TEAM_TEAMSNAP_ID, teamsnap_token=TEAMSNAP_TOKEN)
# r = syncengine.import_items()

class TestSync(TestCase):
    fixtures = ['minimal']

    def setUp(self):
        self.syncengine = TeamsnapSyncEngine(managed_team_teamsnap_id=TEAM_TEAMSNAP_ID, teamsnap_token=TEAMSNAP_TOKEN)
        r = self.syncengine.import_items()
        pass

    def test_syncengine(self):
        # test that the import can be run again
        r = self.syncengine.import_items()
        benchcoach_objects = {
            'availability': list(benchcoach.models.Availability.objects.all()),
            'event': list(benchcoach.models.Event.objects.all()),
            'player': list(benchcoach.models.Player.objects.all()),
            'positioning': list(benchcoach.models.Positioning.objects.all()),
            'team': list(benchcoach.models.Team.objects.all()),
            'venue': list(benchcoach.models.Venue.objects.all())
        }
        teamsnap_objects = {
            'availability': list(teamsnap.models.Availability.objects.all()),
            'event': list(teamsnap.models.Event.objects.all()),
            'member': list(teamsnap.models.Member.objects.all()),
            'lineupentry': list(teamsnap.models.LineupEntry.objects.all()),
            'team': list(teamsnap.models.Team.objects.all()),
            'opponent': list(teamsnap.models.Opponent.objects.all()),
            'location': list(teamsnap.models.Location.objects.all())
        }
        self.assertIsNotNone(r)

    def test_all_models(self):
        pass
        self.syncengine.sync(qs=benchcoach.models.Event.objects.all())
        breakpoint()
        pass