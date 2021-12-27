import django.db.models
from typing import List, Tuple
from benchcoach.models import Availability, Player, Team, Positioning, Event, Venue
from teamsnap.teamsnap.api import TeamSnap
import teamsnap.models

from benchcoach.utils.sync_engine import AbstractSyncEngine

class TeamsnapSyncEngine(AbstractSyncEngine):
    models = [Availability, Player, Team, Positioning, Event, Venue]

    def __init__(self, managed_team_teamsnap_id, teamsnap_token):
        self.managed_teamsnap_team_id = managed_team_teamsnap_id
        self.client = TeamSnap(token=teamsnap_token)

    model_map = {
        Availability: teamsnap.models.Availability,
        Player: teamsnap.models.Member,
        Team: teamsnap.models.Team,
        Positioning: teamsnap.models.LineupEntry,
        Event: teamsnap.models.Event,
        Venue: teamsnap.models.Location
    }

    def _update_teamsnapdb_from_teamsnapapi(self, teamsnap_instance):
        teamsnap_model = teamsnap_instance._meta.model
        new_data = teamsnap_instance.ApiObject.get(client=self.client, id=teamsnap_instance.id).data
        obj, created = teamsnap_model.update_or_create_from_teamsnap_api(new_data)
        return [(obj, created)]

    def _update_teamsnapdb_to_benchcoachdb(self, benchcoach_instance, teamsnap_instance,
                                           create_if_doesnt_exist: bool = False) -> List[Tuple[django.db.models.Model, bool]]:
        ''' Function to update from a teamsnap object to Benchcoach object.

        :param d: The information to update.
        :param teamsnap_object: The teamsnap object from which to update.
        :param create_benchcoach_object: If true, will create the benchcoach object if it doesn't exist
        :param create_related: This is here for decoration only. It doesn't do anything.
        :return: a list of tuples in the form (obj, did_create) for created or modified objects.
        '''

        if isinstance(teamsnap_instance, teamsnap.models.Event):
            benchcoach_model = Event

            d = {
                'start': teamsnap_instance.start_date,
            }

            if teamsnap_instance.team:
                if teamsnap_instance.team.benchcoach_object:
                    if teamsnap_instance.game_type == "Home":
                        d['home_team'] = teamsnap_instance.team.benchcoach_object
                    elif teamsnap_instance.game_type == "Away":
                        d['away_team'] = teamsnap_instance.team.benchcoach_object
                elif not teamsnap_instance.team.benchcoach_object:
                    raise Team.DoesNotExist

            if teamsnap_instance.opponent:
                if teamsnap_instance.opponent.benchcoach_object:
                    if teamsnap_instance.game_type == 'Home':
                        d['away_team'] = teamsnap_instance.opponent.benchcoach_object
                    elif teamsnap_instance.game_type == 'Away':
                        d['home_team'] = teamsnap_instance.opponent.benchcoach_object
                elif not teamsnap_instance.opponent.benchcoach_object:
                    raise Team.DoesNotExist

            if teamsnap_instance.location:
                if teamsnap_instance.location.benchcoach_object:
                    if teamsnap_instance.location:
                        d['venue'] = teamsnap_instance.location.benchcoach_object
                elif not teamsnap_instance.location.benchcoach_object:
                    raise Venue.DoesNotExist

        elif isinstance(teamsnap_instance, teamsnap.models.Opponent):
            benchcoach_model = Team
            d = {
                'name': teamsnap_instance.name,
            }

        elif isinstance(teamsnap_instance, teamsnap.models.Team):
            benchcoach_model = Team
            d = {
                'name': teamsnap_instance.name,
            }

        elif isinstance(teamsnap_instance, teamsnap.models.Location):
            benchcoach_model = Venue
            d = {
                'name': teamsnap_instance.name,
            }

        elif isinstance(teamsnap_instance, teamsnap.models.Member):
            benchcoach_model = Player
            d = {
                'first_name': teamsnap_instance.first_name,
                'last_name': teamsnap_instance.last_name,
                'jersey_number': teamsnap_instance.jersey_number,
            }

        elif isinstance(teamsnap_instance, teamsnap.models.Availability):
            benchcoach_model = Availability

            translation = {
                teamsnap_instance.YES: Availability.YES,
                teamsnap_instance.NO: Availability.NO,
                teamsnap_instance.MAYBE: Availability.MAYBE
            }

            d = {
                'available': translation.get(teamsnap_instance.status_code, Availability.UNKNOWN),
                'player': teamsnap_instance.member.benchcoach_object,
                'event': teamsnap_instance.event.benchcoach_object
            }

            r = []

            if teamsnap_instance.member.benchcoach_object:
                d['player'] = teamsnap_instance.member.benchcoach_object
            elif not teamsnap_instance.member.benchcoach_object:
                raise Availability.DoesNotExist

            if teamsnap_instance.event.benchcoach_object:
                d['event'] = teamsnap_instance.event.benchcoach_object
            elif not teamsnap_instance.event.benchcoach_object:
                raise Event.DoesNotExist

        else:
            raise ValueError

        r=[]
        if teamsnap_instance.benchcoach_object:
            benchcoach_object = benchcoach_model.objects.filter(id=teamsnap_instance.benchcoach_object.id)
            benchcoach_object.update(**d)
            created = False
            r.append((benchcoach_object.first(), created))
        # elif not teamsnap_instance.benchcoach_object and create_if_doesnt_exist:
        elif not teamsnap_instance.benchcoach_object:
            raise django.db.models.Model.DoesNotExist

        return r

    def _find_counterpart(self, instance):
        instance_type = type(instance)
        if instance_type == Availability:
            counterpart_instance = instance.teamsnap_availability

        elif instance_type == Player:
            counterpart_instance = instance.teamsnap_member

        elif instance_type == Event:
            counterpart_instance = instance.teamsnap_event

        elif instance_type == Venue:
            counterpart_instance = instance.teamsnap_location

        elif instance_type == Team:
            if hasattr(instance, 'teamsnap_opponent'):
                counterpart_instance = instance.teamsnap_opponent
            elif hasattr(instance, 'teamsnap_team'):
                counterpart_instance = instance.teamsnap_team
            else:
                raise ValueError("instance doesn't seem to be an teamsnap opponent or a teamsnap team")

        elif instance_type == Positioning:
            counterpart_instance = instance.teamsnap_lineupentry

        if not counterpart_instance: raise Exception()

        return counterpart_instance

    def _fetch_new_data(self, instance):
        api_object = instance.ApiObject.get(client=self.client, id=instance.id)
        return api_object.data

    def _fetch_sync(self, instance):
        r=[]
        counterpart_instance = self._find_counterpart(instance)
        r += self._update_teamsnapdb_from_teamsnapapi(counterpart_instance)
        r += self._update_teamsnapdb_to_benchcoachdb(instance, counterpart_instance)
        return r

    def _sync_qs (self, qs, direction):
        if qs.model not in self.models:
            raise TypeError(f"Sync engine does not sync {qs.model} models")

        r=[]

        for instance in qs:
            r += self._sync_instance(instance, direction=direction)

        return r

    def _sync_instance(self, instance, direction, data=None):
        r=[]
        if direction == 'download':
            r += self._fetch_sync(instance)

        elif direction == 'upload':
            raise NotImplementedError('Uploading not supported by this sync engine yet.')
        else:
            raise TypeError(f"Direction {direction} not supported. 'upload' or 'download' must be specified")

        return r


    def sync(self, qs: django.db.models.QuerySet = None, instance: django.db.models.Model = None,
             direction='download') -> List[Tuple[django.db.models.Model, bool]]:
        if not qs and not instance:
            raise TypeError(f"sync requires either a QuerySet or model instance to be provided")
        if qs and instance:
            raise TypeError(f"sync requires either a QuerySet or model instance to be provided, but not both")
        elif qs:
            r = self._sync_qs(qs, direction)
        elif instance:
            r = self._sync_instance(instance, direction)

        return r

    def import_items(self, object_name):
        Object = {
            obj.__name__.lower(): obj
            for obj in
            [
                teamsnap.models.Availability,
                teamsnap.models.Event,
                teamsnap.models.LineupEntry,
                teamsnap.models.Location,
                teamsnap.models.Member,
                teamsnap.models.Opponent,
                teamsnap.models.Team,
                teamsnap.models.User
            ]
        }.get(object_name)
        if not Object: raise KeyError(f"key {object_name} not found.")
        r = []
        for Obj in [Object]:
            a = Obj.ApiObject.search(self.client, team_id=self.managed_teamsnap_team_id)
            for _a in a:
                obj, created = Obj.update_or_create_from_teamsnap_api(_a.data)
                r += [(obj, created)]

        return r