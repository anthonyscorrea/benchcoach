from django.db import models
from players.models import Player
from events.models import Event
# Create your models here.

class Positioning(models.Model):
   player = models.ForeignKey(Player, on_delete=models.CASCADE)
   event = models.ForeignKey(Event, on_delete=models.CASCADE)
   positions = [
      ('EH', 'EH'),
      ('P', 'P'),
      ('C', 'C'),
      ('1B', '1B'),
      ('2B', '2B'),
      ('3B', '3B'),
      ('SS', 'SS'),
      ('LF', 'LF'),
      ('CF', 'CF'),
      ('RF', 'RF'),
      ('DH','DH')
   ]
   position = models.CharField(choices=positions, default=None, max_length=2, null=True, blank=True)
   order = models.PositiveSmallIntegerField(default=None, null=True, blank=True)

   class Meta:
      unique_together = ('player', 'event',)

class Availability(models.Model):
   YES = 2
   MAYBE = 1
   NO = 0
   UNKNOWN = -1

   event = models.ForeignKey(Event, on_delete=models.CASCADE)
   player = models.ForeignKey(Player, on_delete=models.CASCADE)
   choices = [
      (YES, 'Yes'),
      (NO, 'No'),
      (MAYBE, 'Maybe'),
      (UNKNOWN, 'Unknown')
   ]
   available = models.IntegerField(choices=choices, default=UNKNOWN)

   def __str__(self):
      return f"{self.event}; {self.player}; {self.available}"

   class Meta:
      unique_together = ('event', 'player',)
      verbose_name_plural = "availabilities"