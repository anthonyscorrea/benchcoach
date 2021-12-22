from django.db import models

import benchcoach.models
import teamsnap.teamsnap.api

class TeamsnapBaseModel(models.Model):
   type = None
   id = models.CharField(max_length=50, unique=True, primary_key=True)
   created_at = models.DateTimeField(null=True)
   updated_at = models.DateTimeField(null=True)
   ApiObject = teamsnap.teamsnap.api.ApiObject

   class Meta:
      abstract = True

   def __str__(self):
      return f"TeamSnap {self.__class__.__name__} Object ({self.id})"

   @property
   def api_url(self):
      return "https://api.teamsnap.com/v3/{type}/{id}".format(type=self.type, id=self.id)

class Team(TeamsnapBaseModel):
   type = 'team'
   name = models.CharField(max_length=50, null=True)
   benchcoach_object = models.OneToOneField(
      benchcoach.models.Team,
      null=True,
      blank=True,
      on_delete=models.CASCADE,
      related_name="teamsnap_team"
   )
   ApiObject = teamsnap.teamsnap.api.Team

   @classmethod
   def update_or_create_from_teamsnap_api(cls, teamsnap_data):
      fields = ['id', 'name', 'created_at', 'updated_at']
      data = {k: teamsnap_data[k] for k in fields}
      id = data.pop('id')
      team, created = cls.objects.update_or_create(id=id, defaults=data)
      return (team, created)

class User(TeamsnapBaseModel):
   type = 'user'
   first_name = models.CharField(max_length=50, null=True)
   last_name = models.CharField(max_length = 50, null=True)
   email = models.EmailField(null=True)
   managed_teams = models.ManyToManyField(Team)
   ApiObject = teamsnap.teamsnap.api.User

   @classmethod
   def update_or_create_from_teamsnap_api(cls, teamsnap_data):
      fields = ['id', 'first_name', 'last_name', 'email']
      user_data = {k:teamsnap_data[k] for k in fields}
      managed_teams = []
      for managed_team_id in teamsnap_data['managed_team_ids']:
         obj, created = Team.objects.get_or_create(id=managed_team_id)
         managed_teams.append(obj)
         pass
      id = user_data.pop('id')
      user, created = cls.objects.update_or_create(id=id, defaults=user_data)
      user.managed_teams.add(*managed_teams)
      return (user, created)

class TeamsnapManagedObjectModel(TeamsnapBaseModel):
   team = models.ForeignKey(
      Team,
      verbose_name="managed by team",
      null=True,
      on_delete=models.CASCADE,
   )

   class Meta:
      abstract = True

   @property
   def url(self, endpoint='view'):
      return f"https://go.teamsnap.com/{self.team.id}/{self.type}/{endpoint}/{self.id}"

class Opponent(TeamsnapManagedObjectModel):
   type = 'opponent'
   name = models.CharField(max_length=50, null=True)
   benchcoach_object = models.OneToOneField(
      benchcoach.models.Team,
      null=True,
      blank=True,
      on_delete=models.CASCADE,
      related_name="teamsnap_opponent"
   )
   ApiObject = teamsnap.teamsnap.api.Opponent

   @classmethod
   def update_or_create_from_teamsnap_api(cls, teamsnap_data):
      fields = ['id', 'name', 'created_at', 'updated_at']
      opponent_data = {k: teamsnap_data[k] for k in fields}
      team, created = Team.objects.get_or_create(id=teamsnap_data['team_id'])
      id = opponent_data.pop('id')
      opponent, created = cls.objects.update_or_create(id=id, defaults=opponent_data)
      opponent.team = team
      opponent.save()
      return (opponent, created)

class Location(TeamsnapManagedObjectModel):
   type = 'location'
   name = models.CharField(max_length=50, null=True)
   benchcoach_object = models.OneToOneField(
      benchcoach.models.Venue,
      null=True,
      blank=True,
      on_delete=models.CASCADE,
      related_name="teamsnap_location"
   )
   ApiObject = teamsnap.teamsnap.api.Location

   @classmethod
   def update_or_create_from_teamsnap_api(cls, teamsnap_data):
      fields = ['id', 'name', 'created_at', 'updated_at']
      opponent_data = {k: teamsnap_data[k] for k in fields}
      team, created = Team.objects.get_or_create(id=teamsnap_data['team_id'])
      id = opponent_data.pop('id')
      location, created = cls.objects.update_or_create(id=id, defaults=opponent_data)
      location.team = team
      location.save()
      return (location, created)

class Member(TeamsnapManagedObjectModel):
   # url format is
   # f"https://go.teamsnap.com/{self.team.teamsnap_id}/roster/player/{self.teamsnap_id}"
   # f"https://go.teamsnap.com/{self.team.teamsnap_id}/roster/edit/{self.teamsnap_id}"
   type = 'member'
   name = models.CharField(max_length=50, null=True)
   benchcoach_object = models.OneToOneField(
      benchcoach.models.Player,
      null=True,
      blank=True,
      on_delete=models.CASCADE,
      related_name="teamsnap_member"
   )
   first_name = models.CharField(max_length = 50, null=True)
   last_name = models.CharField(max_length = 50, null=True)
   jersey_number = models.IntegerField(null=True)
   is_non_player = models.BooleanField(null=True)
   ApiObject = teamsnap.teamsnap.api.Member

   @classmethod
   def update_or_create_from_teamsnap_api(cls, teamsnap_data):
      fields = ['id', 'created_at', 'updated_at', 'first_name', 'last_name', 'jersey_number','is_non_player']
      member_data = {k: teamsnap_data[k] for k in fields}
      team, created = Team.objects.get_or_create(id=teamsnap_data['team_id'])
      id = member_data.pop('id')
      member, created = cls.objects.update_or_create(id=id, defaults= member_data)
      member.team = team
      member.save()
      return (member, created)

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
   benchcoach_object = models.OneToOneField(
      benchcoach.models.Event,
      null=True,
      blank=True,
      on_delete=models.CASCADE,
      related_name="teamsnap_event"
   )
   label = models.CharField(max_length = 50, null=True)
   start_date = models.DateTimeField(null=True)
   opponent = models.ForeignKey(Opponent, null=True, on_delete=models.CASCADE, related_name="opponent")
   location = models.ForeignKey(Location, null=True, on_delete=models.CASCADE)
   formatted_title = models.CharField(max_length = 50, null=True)
   points_for_opponent = models.PositiveSmallIntegerField(null=True)
   points_for_team = models.PositiveSmallIntegerField(null=True)
   is_game = models.BooleanField(null=True)
   game_type = models.CharField(max_length = 50, null=True)
   ApiObject = teamsnap.teamsnap.api.Event

   @classmethod
   def update_or_create_from_teamsnap_api(cls, teamsnap_data):
      fields = [
         'id',
         'created_at',
         'updated_at',
         'label',
         'start_date',
         'formatted_title',
         'points_for_opponent',
         'points_for_team',
         'is_game',
         'game_type'
      ]
      event_data = {k: teamsnap_data[k] for k in fields}
      location, created = Location.objects.get_or_create(id=teamsnap_data['location_id'])
      team, created = Team.objects.get_or_create(id=teamsnap_data['team_id'])
      id = event_data.pop('id')
      event, created = cls.objects.update_or_create(id=id, defaults=event_data)
      event.location = location
      if teamsnap_data['opponent_id']:
         opponent, created = Opponent.objects.get_or_create(id=teamsnap_data['opponent_id'])
         event.opponent = opponent
      event.team = team
      event.save()
      return (team, created)

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
   event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
   member = models.ForeignKey(Member, null=True, on_delete=models.CASCADE)
   benchcoach_object = models.OneToOneField(
      benchcoach.models.Availability,
      null=True,
      blank=True,
      on_delete=models.CASCADE,
      related_name="teamsnap_availability"
   )
   status_code = models.SmallIntegerField(null=True, choices=status_codes, default=None)
   ApiObject = teamsnap.teamsnap.api.Availability

   def __str__(self):
      return f"{self.member} - {self.event} ({self.id})"

   class Meta:
      verbose_name_plural = "availabilities"

   @classmethod
   def update_or_create_from_teamsnap_api(cls, teamsnap_data):
      fields = [
         'id',
         'created_at',
         'updated_at',
         'status_code'
      ]
      availability_data = {k: teamsnap_data[k] for k in fields}
      member, created = Member.objects.get_or_create(id=teamsnap_data['member_id'])
      team, created = Team.objects.get_or_create(id=teamsnap_data['team_id'])
      event, created = Event.objects.get_or_create(id=teamsnap_data['event_id'])
      id = availability_data.pop('id')
      availability, created = cls.objects.update_or_create(id=id, defaults=availability_data)
      availability.team = team
      availability.event = event
      availability.member = member
      availability.save()
      return (availability, created)

class LineupEntry(TeamsnapManagedObjectModel):
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
   benchcoach_object = models.OneToOneField(
      benchcoach.models.Positioning,
      null=True,
      blank=True,
      on_delete=models.CASCADE,
      related_name="teamsnap_lineupentry"
   )
   label = models.PositiveSmallIntegerField(choices=positions, default=None, null=True, blank=True)
   sequence = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
   ApiObject = teamsnap.teamsnap.api.EventLineupEntry

   @classmethod
   def update_or_create_from_teamsnap_api(cls, teamsnap_data):
      fields = [
         'id',
         'created_at',
         'updated_at',
         'label',
         'sequence'
      ]
      lineup_entry_data = {k: teamsnap_data[k] for k in fields}
      member, created = Member.objects.get_or_create(id=teamsnap_data['member_id'])
      team, created = Team.objects.get_or_create(id=teamsnap_data['team_id'])
      event, created = Event.objects.get_or_create(id=teamsnap_data['event_id'])
      id = lineup_entry_data.pop('id')
      lineup_entry, created = cls.objects.update_or_create(id=id, defaults=lineup_entry_data)
      lineup_entry.team = team
      lineup_entry.event = event
      lineup_entry.member = member
      lineup_entry.save()
      return (lineup_entry, created)