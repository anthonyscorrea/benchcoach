from django.db import models

import lineups.models
import teams.models
import venues.models
import players.models
import events.models

class TeamsnapBaseModel(models.Model):
   teamsnap_id = models.CharField(max_length=10, unique=True)
   name = models.CharField(max_length=50, null=True)

   class Meta:
      abstract = True

   def __str__(self):
      return f"{self.name} ({self.teamsnap_id})"

class User(TeamsnapBaseModel):
   access_token = models.CharField(max_length = 50)
   name = None

   def __str__(self):
      return f"{self.teamsnap_id}"

class Team(TeamsnapBaseModel):
   bencoach_team = models.ForeignKey(teams.models.Team, null=True, on_delete=models.CASCADE)

   @property
   def view_url(self):
      return f"https://go.teamsnap.com/{self.team.teamsnap_id}/team/view/{self.teamsnap_id}"

   @property
   def edit_url(self):
      return f"https://go.teamsnap.com/{self.team.teamsnap_id}/team/edit/{self.teamsnap_id}"

class Location(TeamsnapBaseModel):
   benchcoach_venue = models.ForeignKey(venues.models.Venue, null=True, on_delete=models.CASCADE)

   @property
   def view_url(self):
      return f"https://go.teamsnap.com/{self.team.teamsnap_id}/location/view/{self.teamsnap_id}"

   @property
   def edit_url(self):
      return f"https://go.teamsnap.com/{self.team.teamsnap_id}/location/edit/{self.teamsnap_id}"

class Member(TeamsnapBaseModel):
   name = None
   benchcoach_player = models.ForeignKey(players.models.Player, null=True, on_delete=models.CASCADE)
   team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)
   first_name = models.CharField(max_length = 50, null=True)
   last_name = models.CharField(max_length = 50, null=True)
   jersey_number = models.IntegerField(null=True)
   is_non_player = models.BooleanField()

   def __str__(self):
      return f"{self.last_name}, {self.first_name} ({self.teamsnap_id})"

   @property
   def view_url(self):
      return f"https://go.teamsnap.com/{self.team.teamsnap_id}/roster/player/{self.teamsnap_id}"

   @property
   def edit_url(self):
      return f"https://go.teamsnap.com/{self.team.teamsnap_id}/roster/edit/{self.teamsnap_id}"

class Event(TeamsnapBaseModel):
   benchcoach_event = models.ForeignKey(events.models.Event, null=True, on_delete=models.CASCADE)
   label = models.CharField(max_length = 50, null=True)
   start_date = models.DateTimeField(null=True)
   opponent = models.ForeignKey(Team, null=True, on_delete=models.CASCADE, related_name="opponent")
   team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)
   location = models.ForeignKey(Location, null=True, on_delete=models.CASCADE)
   formatted_title = models.CharField(max_length = 50, null=True)
   points_for_opponent = models.PositiveSmallIntegerField(null=True)
   points_for_team = models.PositiveSmallIntegerField(null=True)
   is_game = models.BooleanField()

   @property
   def view_url(self):
      return f"https://go.teamsnap.com/{self.team.teamsnap_id}/schedule/view_game/{self.teamsnap_id}"

   @property
   def edit_url(self):
      return f"https://go.teamsnap.com/{self.team.teamsnap_id}/schedule/edit_game/{self.teamsnap_id}"

   def __str__(self):
      return f"{self.formatted_title} ({self.teamsnap_id})"

class Availability(TeamsnapBaseModel):
   status_codes = [
      (1, 'Yes'),
      (0, 'No'),
      (2, 'Maybe'),
      (None, 'Unknown')
   ]
   name = None
   team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)
   event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
   member = models.ForeignKey(Member, null=True, on_delete=models.CASCADE)
   benchcoach_availability =  models.ForeignKey(lineups.models.Availability, null=True, on_delete=models.CASCADE)
   status_code = models.SmallIntegerField(null=True, choices=status_codes, default=None)

   def __str__(self):
      return f"{self.member} - {self.event} ({self.teamsnap_id})"

   class Meta:
      verbose_name_plural = "availabilities"

class LineupEntry(TeamsnapBaseModel):
   name = None
   teamsnap_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
   member = models.ForeignKey(Member, on_delete=models.CASCADE)
   event = models.ForeignKey(Event, on_delete=models.CASCADE)
   positions = [
      (11, 'EH'),
      (1, 'P'),
      (2, 'C'),
      (3, '1B'),
      (4, '2B'),
      (5, '3B'),
      (6, 'SS'),
      (7, 'LF'),
      (8, 'CF'),
      (9, 'RF'),
      (10,'DH')
   ]
   label = models.PositiveSmallIntegerField(choices=positions, default=None, null=True, blank=True)
   sequence = models.PositiveSmallIntegerField(default=0, null=True, blank=True)

   class Meta:
      unique_together = ('member', 'event',)
