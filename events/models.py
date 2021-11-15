from django.db import models
from venues.models import Venue
from teams.models import Team
from players.models import Player, StatLine

class Event(models.Model):
   start = models.DateTimeField(null=True)
   venue = models.ForeignKey(Venue, null=True, on_delete=models.CASCADE)
   home_team = models.ForeignKey(Team, null=True,on_delete=models.CASCADE, related_name="home_team")
   away_team = models.ForeignKey(Team, null=True,on_delete=models.CASCADE, related_name="away_team")

   def __str__(self):
      return f"{self.start:%Y-%m-%d %H:%M}"

class Season(models.Model):
   name = models.CharField(max_length=50)