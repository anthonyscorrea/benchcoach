from django.db import models
from players.models import Player
from events.models import Event
# Create your models here.
class Positioning(models.Model):
   player = models.ForeignKey(Player, on_delete=models.CASCADE)
   event = models.ForeignKey(Event, on_delete=models.CASCADE)
   positions = [
      ('P', 'P'),
      ('C', 'C'),
      ('1B', '1B'),
      ('2B', '2B'),
      ('3B', '3B'),
      ('SS', 'SS'),
      ('LF', 'LF'),
      ('CF', 'CF'),
      ('RF', 'RF'),
      ('DH','DH'),
      ('EH','EH')
   ]
   position = models.CharField(choices=positions, default=None, max_length=2, null=True)
   order = models.IntegerField(default=None, null=True)

   class Meta:
      unique_together = ('player', 'event',)