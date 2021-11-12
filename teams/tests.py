from django.urls import reverse
from django.test import TestCase
from .models import Team

# Create your tests here.
class TestTeamModel(TestCase):
    fixtures = ['blaseball']

    def test_query_team(self):
        """
        Return the desired team
        """
        team = Team.objects.get(id=1)
        self.assertEqual(team.name, "Chicago Firefighters")

class TestTeamViews(TestCase):
    fixtures = ['blaseball']

    def test_team_list(self):
        response = self.client.get(reverse('teams list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn({'id':1, 'title':'Chicago Firefighters'}, response.context['items'])
        self.assertIn({'id':2, 'title':'Boston Flowers'}, response.context['items'])
        self.assertIn({'id':24, 'title':'Baltimore Crabs'}, response.context['items'])

    def test_team_edit(self):
        response = self.client.get(reverse('edit team', args=[1]))
        self.assertEqual(response.status_code, 200)

        #create new team
        response = self.client.post(reverse('edit team', args=[0]), data={'name': "A new team"})
        self.assertEqual(201, response.status_code)
        new_team = Team.objects.get(id=response.context['id'])
        self.assertEqual('A new team',new_team.name, )

        # modify team
        response = self.client.post(reverse('edit team', args=[1]), data={'name': "A different team name"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context['id'])
        modified_team = Team.objects.get(id=response.context['id'])
        self.assertEqual('A different team name', modified_team.name)