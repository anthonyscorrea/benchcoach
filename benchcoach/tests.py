from django.test import TestCase
from .models import Event, Player, Team, Venue, Positioning
from .forms import PositioningFormSet
from datetime import datetime
from django.urls import reverse

FIXTURES = ["blaseball"]


class TestEventModel(TestCase):
    fixtures = FIXTURES

    def test_query_event(self):
        """
        Return the desired event
        """
        event = Event.objects.get(id=1)
        self.assertEqual("Chicago Firefighters", event.away_team.name)
        self.assertEqual("Dallas Steaks", event.home_team.name)
        self.assertEqual("George Fourman Stadium", event.venue.name)
        self.assertEqual(
            datetime(year=2020, month=8, day=24, hour=16, minute=0, second=1),
            event.start,
        )


class TestEventViews(TestCase):
    fixtures = FIXTURES

    def test_event_list(self):
        response = self.client.get(reverse("schedule"))
        self.assertEqual(200, response.status_code)

    def test_event_edit(self):
        response = self.client.get(reverse("edit event", args=[2]))
        self.assertEqual(200, response.status_code)

        # create new event
        new_event_data = {
            "home_team": 23,
            "away_team": 24,
            "start": datetime(year=2021, month=1, day=1, hour=9, minute=0, second=0),
            "venue": 19,
        }

        response = self.client.post(
            reverse("edit event", args=[0]), data=new_event_data
        )
        self.assertEqual(201, response.status_code)
        new_event = Event.objects.get(id=response.context["id"])
        self.assertEqual(new_event_data["home_team"], new_event.home_team.id)
        self.assertEqual(new_event_data["away_team"], new_event.away_team_id)
        self.assertEqual(new_event_data["start"], new_event.start)

        # modify event
        modified_event_data = {
            "home_team": 23,
            "away_team": 24,
            "start": datetime(year=2021, month=1, day=1, hour=9, minute=0, second=0),
            "venue": 19,
        }
        response = self.client.post(
            reverse("edit event", args=[1]), data=modified_event_data
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["id"])
        modified_event = Event.objects.get(id=response.context["id"])

        self.assertEqual(modified_event_data["home_team"], modified_event.home_team.id)
        self.assertEqual(modified_event_data["away_team"], modified_event.away_team.id)
        self.assertEqual(modified_event_data["start"], modified_event.start)
        self.assertEqual(modified_event_data["venue"], modified_event.venue.id)


class TestVenueViews(TestCase):
    fixtures = ["blaseball"]

    def test_positioning_list(self):
        response = self.client.get(reverse("edit lineup", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_positioning_formset(self):
        event = 1

        sample_data = [
            # first player positioning
            (1, Player.objects.get(id=1).id, "P"),
            (2, Player.objects.get(id=2).id, "C"),
            (3, Player.objects.get(id=3).id, "1B"),
        ]
        data = {}

        for i, (order, player, position) in enumerate(sample_data):
            data[f"form-{i}-order"] = order
            data[f"form-{i}-player"] = player
            data[f"form-{i}-position"] = position

        management = {
            "form-INITIAL_FORMS": "0",
            "form-TOTAL_FORMS": len(sample_data),
            "form-MAX_NUM_FORMS": "",
        }

        formset = PositioningFormSet({**management, **data})

        self.assertTrue(formset.is_valid())
        for form in formset:
            self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse("edit lineup", args=[event]), {**management, **data}
        )

        self.assertEqual(response.status_code, 200)

        for d in sample_data:
            with self.subTest(d):
                p = Positioning.objects.get(player_id=d[1], event_id=event)
                self.assertEqual(d[0], p.order)
                self.assertEqual(d[2], p.position)
        pass


class TestPlayerModel(TestCase):
    fixtures = FIXTURES

    def test_query_player(self):
        """
        Return the desired player
        """
        player = Player.objects.get(id=1)
        self.assertEqual(player.first_name, "Edric")
        self.assertEqual(player.last_name, "Tosser")
        self.assertEqual(player.jersey_number, 1)
        self.assertEqual(player.team.name, "Chicago Firefighters")


class TestPlayerViews(TestCase):
    fixtures = FIXTURES

    def test_player_list(self):
        response = self.client.get(reverse("players list"))
        self.assertEqual(response.status_code, 200)

    def test_player_edit(self):
        response = self.client.get(reverse("edit player", args=[1]))
        self.assertEqual(response.status_code, 200)

        # create new player
        new_player_data = {
            "first_name": "A new player first name",
            "last_name": "A new player last name",
            "jersey_number": 99,
            "team": 1,
        }

        response = self.client.post(
            reverse("edit player", args=[0]), data=new_player_data
        )
        self.assertEqual(201, response.status_code)
        new_player = Player.objects.get(id=response.context["id"])
        self.assertEqual(new_player_data["first_name"], new_player.first_name)
        self.assertEqual(new_player_data["last_name"], new_player.last_name)

        # modify player
        modified_player_data = {
            "first_name": "A changed player first name",
            "last_name": "A changed player last name",
            "jersey_number": 99,
            "team": 1,
        }
        response = self.client.post(
            reverse("edit player", args=[1]), data=modified_player_data
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["id"])
        modified_player = Player.objects.get(id=response.context["id"])
        self.assertEqual(modified_player_data["first_name"], modified_player.first_name)
        self.assertEqual(modified_player_data["last_name"], modified_player.last_name)


class TestTeamModel(TestCase):
    fixtures = ["blaseball"]

    def test_query_team(self):
        """
        Return the desired team
        """
        team = Team.objects.get(id=1)
        self.assertEqual(team.name, "Chicago Firefighters")


class TestTeamViews(TestCase):
    fixtures = ["blaseball"]

    def test_team_list(self):
        response = self.client.get(reverse("teams list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            {"id": 1, "title": "Chicago Firefighters"}, response.context["items"]
        )
        self.assertIn({"id": 2, "title": "Boston Flowers"}, response.context["items"])
        self.assertIn({"id": 24, "title": "Baltimore Crabs"}, response.context["items"])

    def test_team_edit(self):
        response = self.client.get(reverse("edit team", args=[1]))
        self.assertEqual(response.status_code, 200)

        # create new team
        response = self.client.post(
            reverse("edit team", args=[0]), data={"name": "A new team"}
        )
        self.assertEqual(201, response.status_code)
        new_team = Team.objects.get(id=response.context["id"])
        self.assertEqual(
            "A new team",
            new_team.name,
        )

        # modify team
        response = self.client.post(
            reverse("edit team", args=[1]), data={"name": "A different team name"}
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["id"])
        modified_team = Team.objects.get(id=response.context["id"])
        self.assertEqual("A different team name", modified_team.name)


class TestVenueModel(TestCase):
    fixtures = ["blaseball"]

    def test_query_venue(self):
        """
        Return the desired venue
        """
        venue = Venue.objects.get(id=1)
        self.assertEqual(venue.name, "Chesapeake Racetrack and Ballpark")


class TestVenueViews(TestCase):
    fixtures = ["blaseball"]

    def test_venue_list(self):
        response = self.client.get(reverse("venues list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            {"id": 1, "title": "Chesapeake Racetrack and Ballpark"},
            response.context["items"],
        )
        self.assertIn(
            {"id": 2, "title": "Tokyo Fitness Center"}, response.context["items"]
        )
        self.assertIn(
            {"id": 25, "title": "ILB Historical Preservation Site"},
            response.context["items"],
        )

    def test_venue_edit(self):
        response = self.client.get(reverse("edit venue", args=[1]))
        self.assertEqual(response.status_code, 200)

        # create new venue
        response = self.client.post(
            reverse("edit venue", args=[0]), data={"name": "A new venue"}
        )
        self.assertEqual(201, response.status_code)
        new_venue = Venue.objects.get(id=response.context["id"])
        self.assertEqual(
            "A new venue",
            new_venue.name,
        )

        # modify venue
        response = self.client.post(
            reverse("edit venue", args=[1]), data={"name": "A different venue name"}
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["id"])
        modified_venue = Venue.objects.get(id=response.context["id"])
        self.assertEqual("A different venue name", modified_venue.name)
