from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from .models import Event

FIXTURES = ['sample_events.yaml', 'sample_teams.yaml']

class TestEventModel(TestCase):
    fixtures = FIXTURES

    def test_query_event(self):
        """
        Return the desired event
        """
        event = Event.objects.get(id=1)
        # self.assertEqual(event.first_name, "Edric")
        # self.assertEqual(event.last_name, "Tosser")
        # self.assertEqual(event.jersey_number, 1)
        # self.assertEqual(event.team.name, "Chicago Firefighters")

class TestEventViews(TestCase):
    fixtures = FIXTURES

    def test_event_list(self):
        response = self.client.get(reverse('schedule'))
        self.assertEqual(response.status_code, 200)

    def test_event_edit(self):
        response = self.client.get(reverse('edit event', args=[2]))
        self.assertEqual(response.status_code, 200)

