from django.test import TestCase, Client
from django.urls import reverse
from .models import Player

FIXTURES = ['blaseball']

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
        response = self.client.get(reverse('players list'))
        self.assertEqual(response.status_code, 200)

    def test_player_edit(self):
        response = self.client.get(reverse('edit player', args=[1]))
        self.assertEqual(response.status_code, 200)

        # create new player
        new_player_data = {
            'first_name': "A new player first name",
            'last_name': "A new player last name",
            'jersey_number':99,
            'team':1
        }

        response = self.client.post(reverse('edit player', args=[0]), data=new_player_data)
        self.assertEqual(201, response.status_code)
        new_player = Player.objects.get(id=response.context['id'])
        self.assertEqual(new_player_data['first_name'], new_player.first_name)
        self.assertEqual(new_player_data['last_name'], new_player.last_name)

        # modify player
        modified_player_data = {
            'first_name': "A changed player first name",
            'last_name': "A changed player last name",
            'jersey_number': 99,
            'team': 1
        }
        response = self.client.post(reverse('edit player', args=[1]), data=modified_player_data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context['id'])
        modified_player = Player.objects.get(id=response.context['id'])
        self.assertEqual(modified_player_data['first_name'], modified_player.first_name)
        self.assertEqual(modified_player_data['last_name'], modified_player.last_name)

