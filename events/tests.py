from django.test import TestCase
from events.models import Player, Event, Availability, Team, Positioning
import datetime
import pytz
# Create your tests here.

class BenchcoachTestCase(TestCase):
    def setUp(self):
        for first_name, last_name, jersey_number in [
            ("Rush", "Valenzuela", 1),
            ("Baby", "Triumphant", 2)
        ]:
            Player.objects.create(first_name=first_name, last_name=last_name, jersey_number=jersey_number)

        for name in ["Firefighters", "Garages"]:
            Team.objects.create(name=name)

        for start, home_team_id, away_team_id in [
            (datetime.datetime(2020, 1, 2, 12, 0), 1, 2), # id = 1
            (datetime.datetime(2020, 1, 3, 12, 0), 2, 1), # id = 2
            (datetime.datetime(2020, 1, 4, 12, 0), 2, 1) # id = 3
        ]:
            Event.objects.create(start=start, home_team_id=home_team_id, away_team_id=away_team_id)

        for event_id in [
            1
        ]:
            for player_id, available in [
                (1,"Yes"),
                (2,"No")
            ]:
                Availability.objects.create(event_id=event_id, player_id=player_id, available=available)

        for event_id in [
            1
        ]:
            for player_id, position in [
                (1, "C"),
                (2, "1B")
            ]:
                Positioning.objects.create(event_id=event_id, player_id=player_id, position=position)

        for event_id in [
            2
        ]:
            for player_id, available in [
                (1,"Yes"),
                (2,"Yes")
            ]:
                Availability.objects.create(event_id=event_id, player_id=player_id, available=available)

        for event_id in [
            3
        ]:
            for player_id, available in [
                (1,"No"),
                (2,"No")
            ]:
                Availability.objects.create(event_id=event_id, player_id=player_id, available=available)
        pass


    def test_player(self):
        """Test that player works"""
        player_1 = Player.objects.get(first_name="Rush")
        player_2 = Player.objects.get(first_name="Baby")
        self.assertEqual(str(player_1), f"Valenzuela, Rush")
        self.assertEqual(str(player_2), f"Triumphant, Baby")
        pass

    def test_event(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(event.start.year, 2020)
        self.assertEqual(event.start.month, 1)
        self.assertEqual(event.start.day, 2)
        self.assertEqual(event.start.hour, 12)
        self.assertEqual(event.start.minute, 0)
        self.assertEqual(event.home_team.name, "Firefighters")
        self.assertEqual(event.away_team.name, "Garages")

    def test_availability(self):
        availability_1 = Availability.objects.get(event_id=1, player_id=1)
        availability_2 = Availability.objects.get(event_id=1, player_id=2)

        self.assertEqual(availability_1.available, "Yes")
        self.assertEqual(availability_2.available, "No")
        pass

    def test_positioning(self):
        positioning_1 = Positioning.objects.get(event_id=1, player_id=1)
        positioning_2 = Positioning.objects.get(event_id=1, player_id=2)
        # positing_1
        pass

    def test_combine_info(self):
        event = Event.objects.get(pk=1)
        event_id = 1
        player_query = Player.objects.all()
        positioning_query = Positioning.objects.filter(event=event).select_related('player')
        availability_query = Availability.objects.filter(event=event).select_related('player')
        player_event_info = []

        for player in player_query:
            player_event_info.append(
                {
                    "player":player,
                    "positioning":positioning_query.get(player_id=player.id),
                    "availability":availability_query.get(player_id=player.id)
                }
            )

        pass
