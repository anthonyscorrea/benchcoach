from django.test import TestCase
from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from .models import Positioning, Player
from .forms import PositioningFormSet

class TestVenueViews(TestCase):
    fixtures = ['blaseball']

    def test_positioning_list(self):
        response = self.client.get(reverse('edit lineup', args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_positioning_formset(self):
        formset = PositioningFormSet({
            'form-0-id':1,
            'form-0-order':0,
            'form-0-player':Player.objects.get(id=1),
            'form-0-position':'P'
        })
        self.assertTrue(formset.is_valid())