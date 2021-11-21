from django.db import models
import teams.models
import venues.models
import players.models
import events.models

class TeamsnapBaseModel(models.Model):
   teamsnap_id = models.CharField(max_length=10, unique=True)
   name = models.CharField(max_length=50, null=True)

   class Meta:
      abstract = True

class User(TeamsnapBaseModel):
   access_token = models.CharField(max_length = 50)
   name = None

class Team(TeamsnapBaseModel):
   team = models.ForeignKey(teams.models.Team, null=True, on_delete=models.CASCADE)

class Location(TeamsnapBaseModel):
   venue = models.ForeignKey(venues.models.Venue, null=True, on_delete=models.CASCADE)

class Member(TeamsnapBaseModel):
   player = models.ForeignKey(players.models.Player, null=True, on_delete=models.CASCADE)

class Event(TeamsnapBaseModel):
   event = models.ForeignKey(events.models.Event, null=True, on_delete=models.CASCADE)
   label = models.CharField(max_length = 50, null=True)
   start_date = models.DateTimeField(null=True)
   opponent = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)
   location = models.ForeignKey(Location, null=True, on_delete=models.CASCADE)
   formatted_title = models.CharField(max_length = 50, null=True)