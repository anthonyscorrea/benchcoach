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

class Availability(models.Model):
   event = models.ForeignKey(Event, on_delete=models.CASCADE)
   player = models.ForeignKey(Player, on_delete=models.CASCADE)
   choices = [
      ('Yes', 'YES'),
      ('No', 'NO'),
      ('Maybe', 'MAY'),
      ('Unknown', 'UNK')
   ]
   available = models.CharField(choices=choices, default='UNK',max_length = 7)

   def __str__(self):
      return f"{self.event}; {self.player}; {self.available}"

   class Meta:
      unique_together = ('event', 'player',)
      verbose_name_plural = "availabilities"

class Season(models.Model):
   name = models.CharField(max_length=50)