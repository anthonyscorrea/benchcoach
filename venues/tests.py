from django.test import TestCase
from django.urls import reverse
from .models import Venue

class TestVenueModel(TestCase):
    fixtures = ['blaseball']

    def test_query_venue(self):
        """
        Return the desired venue
        """
        venue = Venue.objects.get(id=1)
        self.assertEqual(venue.name, "Chesapeake Racetrack and Ballpark")

class TestVenueViews(TestCase):
    fixtures = ['blaseball']

    def test_venue_list(self):
        response = self.client.get(reverse('venues list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn({'id':1, 'title':'Chesapeake Racetrack and Ballpark'}, response.context['items'])
        self.assertIn({'id':2, 'title':'Tokyo Fitness Center'}, response.context['items'])
        self.assertIn({'id':25, 'title':'ILB Historical Preservation Site'}, response.context['items'])

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