from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from .models import Venue

FIXTURES = ['sample_venues.yaml']

class TestVenueModel(TestCase):
    fixtures = FIXTURES

    def test_query_venue(self):
        """
        Return the desired venue
        """
        venue = Venue.objects.get(id=1)
        self.assertEqual(venue.name, "Chesapeake Racetrack and Ballpark")

class TestVenueViews(TestCase):
    fixtures = FIXTURES

    def test_venue_list(self):
        response = self.client.get(reverse('venues list'))
        self.assertEqual(response.status_code, 200)

    def test_venue_edit(self):
        response = self.client.get(reverse('edit venue', args=[1]))
        self.assertEqual(response.status_code, 200)

        #create new venue
        response = self.client.post(reverse('edit venue', args=[0]), data={'name': "A new venue"})
        self.assertEqual(201, response.status_code)
        new_venue = Venue.objects.get(id=response.context['id'])
        self.assertEqual('A new venue',new_venue.name, )

        # modify venue
        response = self.client.post(reverse('edit venue', args=[1]), data={'name': "A different venue name"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context['id'])
        modified_venue = Venue.objects.get(id=response.context['id'])
        self.assertEqual('A different venue name', modified_venue.name)