from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from .models import Event
from datetime import datetime
FIXTURES = ['blaseball']

class TestEventModel(TestCase):
    fixtures = FIXTURES

    def test_query_event(self):
        """
        Return the desired event
        """
        event = Event.objects.get(id=1)
        self.assertEqual("Chicago Firefighters", event.away_team.name)
        self.assertEqual("Dallas Steaks", event.home_team.name)
        self.assertEqual('George Fourman Stadium', event.venue.name)
        self.assertEqual(datetime(
            year=2020,
            month=8,
            day=24,
            hour=16,
            minute=0,
            second=1), event.start)

class TestEventViews(TestCase):
    fixtures = FIXTURES

    def test_event_list(self):
        response = self.client.get(reverse('schedule'))
        self.assertEqual(200, response.status_code)

    def test_event_edit(self):
        response = self.client.get(reverse('edit event', args=[2]))
        self.assertEqual(200, response.status_code)

        # create new event
        new_event_data = {
            'home_team': 23,
            'away_team': 24,
            'start':datetime(
                year=2021,
                month=1,
                day=1,
                hour=9,
                minute=0,
                second=0),
            'venue':19
        }

        response = self.client.post(reverse('edit event', args=[0]), data=new_event_data)
        self.assertEqual(201, response.status_code)
        new_event = Event.objects.get(id=response.context['id'])
        self.assertEqual(new_event_data['home_team'], new_event.home_team.id)
        self.assertEqual(new_event_data['away_team'], new_event.away_team_id)
        self.assertEqual(new_event_data['start'], new_event.start)

        # modify event
        modified_event_data = {
                    'home_team': 23,
                    'away_team': 24,
                    'start':datetime(
                        year=2021,
                        month=1,
                        day=1,
                        hour=9,
                        minute=0,
                        second=0),
                    'venue':19
                }
        response = self.client.post(reverse('edit event', args=[1]), data=modified_event_data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context['id'])
        modified_event = Event.objects.get(id=response.context['id'])

        self.assertEqual(modified_event_data['home_team'], modified_event.home_team.id)
        self.assertEqual(modified_event_data['away_team'], modified_event.away_team.id)
        self.assertEqual(modified_event_data['start'], modified_event.start)
        self.assertEqual(modified_event_data['venue'], modified_event.venue.id)
