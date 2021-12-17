from django.db import models

import lineups.models
import teams.models
import venues.models
import players.models
import events.models

class TeamsnapBaseModel(models.Model):
   type = None
   id = models.CharField(max_length=50, unique=True, primary_key=True)
   name = models.CharField(max_length=50, null=True)
   created_at = models.DateTimeField(null=True)
   updated_at = models.DateTimeField(null=True)

   class Meta:
      abstract = True

   def __str__(self):
      return f"TeamSnap {self.__class__.__name__} Object ({self.id})"

   @property
   def api_url(self):
      return "https://api.teamsnap.com/v3/{type}/{id}".format(type=self.type, id=self.id)

class Team(TeamsnapBaseModel):
   type = 'team'
   managed_by_team = None
   benchcoach_object = models.ForeignKey(teams.models.Team, null=True, on_delete=models.CASCADE,related_name="teamsnapteam")

class User(TeamsnapBaseModel):
   type = 'user'
   name = None
   first_name = models.CharField(max_length=50, null=True)
   last_name = models.CharField(max_length = 50, null=True)
   email = models.EmailField(null=True)
   managed_teams = models.ManyToManyField(Team)

class TeamsnapManagedObjectModel(TeamsnapBaseModel):
   managed_by_team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)

   class Meta:
      abstract = True

   @property
   def url(self, endpoint='view'):
      return f"https://go.teamsnap.com/{self.managed_by_team.id}/{self.type}/{endpoint}/{self.id}"

class Opponent(TeamsnapManagedObjectModel):
   type = 'opponent'
   benchcoach_object = models.ForeignKey(teams.models.Team, null=True, on_delete=models.CASCADE)

class Location(TeamsnapManagedObjectModel):
   benchcoach_object = models.ForeignKey(venues.models.Venue, null=True, on_delete=models.CASCADE)

class Member(TeamsnapManagedObjectModel):
   # url format is
   # f"https://go.teamsnap.com/{self.team.teamsnap_id}/roster/player/{self.teamsnap_id}"
   # f"https://go.teamsnap.com/{self.team.teamsnap_id}/roster/edit/{self.teamsnap_id}"
   type = 'member'
   benchcoach_object = models.ForeignKey(players.models.Player, null=True, on_delete=models.CASCADE)
   first_name = models.CharField(max_length = 50, null=True)
   last_name = models.CharField(max_length = 50, null=True)
   jersey_number = models.IntegerField(null=True)
   is_non_player = models.BooleanField()

   def __str__(self):
      return f"{self.last_name}, {self.first_name} ({self.id})"

   @property
   def name(self):
      return f"{self.first_name} {self.last_name}"

class Event(TeamsnapManagedObjectModel):
   # url is
   # f"https://go.teamsnap.com/{self.team.teamsnap_id}/schedule/view_game/{self.teamsnap_id}"
   # f"https://go.teamsnap.com/{self.team.teamsnap_id}/schedule/edit_game/{self.teamsnap_id}"
   type = 'event'
   name = None
   benchcoach_object = models.ForeignKey(events.models.Event, null=True, on_delete=models.CASCADE, related_name ='teamsnap_event')
   label = models.CharField(max_length = 50, null=True)
   start_date = models.DateTimeField(null=True)
   opponent = models.ForeignKey(Opponent, null=True, on_delete=models.CASCADE, related_name="opponent")
   location = models.ForeignKey(Location, null=True, on_delete=models.CASCADE)
   formatted_title = models.CharField(max_length = 50, null=True)
   points_for_opponent = models.PositiveSmallIntegerField(null=True)
   points_for_team = models.PositiveSmallIntegerField(null=True)
   is_game = models.BooleanField()

   def __str__(self):
      return f"{self.formatted_title} ({self.id})"

class Availability(TeamsnapManagedObjectModel):
   YES = 1
   NO = 0
   MAYBE = 2
   UNKNOWN = None
   status_codes = [
      (YES, 'Yes'),
      (NO, 'No'),
      (MAYBE, 'Maybe'),
      (UNKNOWN, 'Unknown')
   ]
   name = None
   event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
   member = models.ForeignKey(Member, null=True, on_delete=models.CASCADE)
   benchcoach_object =  models.ForeignKey(lineups.models.Availability, null=True, on_delete=models.CASCADE)
   status_code = models.SmallIntegerField(null=True, choices=status_codes, default=None)

   def __str__(self):
      return f"{self.member} - {self.event} ({self.id})"

   class Meta:
      verbose_name_plural = "availabilities"

class LineupEntry(TeamsnapManagedObjectModel):
   name = None
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