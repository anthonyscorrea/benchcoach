from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from .models import Player

FIXTURES = ['sample_players.yaml', 'sample_teams.yaml']

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
        response = self.client.post(reverse('edit player', args=[0]), data={'name': "A new player"})
        self.assertEqual(201, response.status_code)
        new_player = Player.objects.get(id=response.context['id'])
        self.assertEqual('A new player', new_player.name)

        # modify player
        response = self.client.post(reverse('edit player', args=[1]), data={'name': "A different player name"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context['id'])
        modified_player = Player.objects.get(id=response.context['id'])
        self.assertEqual('A different player name', modified_player.name)

