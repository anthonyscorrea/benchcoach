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
        event = 1

        sample_data = [
            # first player positioning
            (1, Player.objects.get(id=1).id, 'P'),
            (2, Player.objects.get(id=2).id, 'C'),
            (3, Player.objects.get(id=3).id, '1B')
        ]
        data = {}

        for i, (order, player, position) in enumerate(sample_data):
            data[f'form-{i}-order']=order
            data[f'form-{i}-player']=player
            data[f'form-{i}-position'] = position

        management = {
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': len(sample_data),
            'form-MAX_NUM_FORMS': ''
        }

        formset = PositioningFormSet({**management, **data})

        self.assertTrue(formset.is_valid())
        for form in formset:
            self.assertTrue(form.is_valid())

        response = self.client.post(reverse('edit lineup', args=[event]), {**management, **data})

        self.assertEqual(response.status_code, 200)

        for d in sample_data:
            with self.subTest(d):
                p = Positioning.objects.get(player_id=d[1], event_id=event)
                self.assertEqual(d[0], p.order)
                self.assertEqual(d[2], p.position)
        pass