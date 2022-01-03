import django.db.models
from typing import List, Tuple

import benchcoach.models
from benchcoach.models import BenchcoachModel, Availability, Player, Team, Positioning, Event, Venue
from teamsnap.teamsnap.api import TeamSnap
import teamsnap.models
from django.db.models import QuerySet

from benchcoach.utils.sync_engine import AbstractSyncEngine

class TeamsnapSyncEngine(AbstractSyncEngine):
    models = [
        Availability,
        Player,
        Team,
        # Positioning, # Not Implemented
        Event,
        Venue
    ]

    def __init__(self, managed_team_teamsnap_id, teamsnap_token):
        self.managed_teamsnap_team_id = managed_team_teamsnap_id
        self.client = TeamSnap(token=teamsnap_token)

    def _bulk_sync_from_teamsnap(self, qs:QuerySet)-> List[BenchcoachModel]:
        '''
        Syncs BenchCoach instances (in the form of a QuerySet) from TeamSnap.
        This function fetches the actual information from teamsnap, then hands it off to the self._update* functions.
        This funciton cuts down on the number of API calls and should be speedier then doing them one by one.
        Upating of models from the data is still done one by one.
        :param benchcoach_instance: instance to be synced
        :return: List of BenchCoach objects that have been processed (but not necessarily changed) during sync.
        '''

        # I hate having this translation. What I really want is just a property for "teamsnap_object"
        # which would simplify all this, but I couldn't figure out how to implement in the
        # teamsnap model foreign key and "related_name" that didn't cause conflicts. I don't
        # think I need to be too much smarter to figure this out, but alas I am not smart enough.
        if qs.model not in self.models:
            raise TypeError(f"Sync engine does not sync {qs.model} models")

        benchcoachmodel_to_teamsnapfield = {
            Availability:'teamsnap_availability',
            Player:'teamsnap_member',
            Team:'teamsnap_opponent',
            # Positioning:'teamsnap_lineupentry', # Not Implemented Yet, but will be 'teamsnap_lineupentry'
            Event:'teamsnap_event',
            Venue:'teamsnap_location'
        }

        teamsnapmodel_to_apiobject = {
            teamsnap.models.Availability: teamsnap.teamsnap.api.Availability,
            teamsnap.models.Event: teamsnap.teamsnap.api.Event,
            # teamsnap.models.LineupEntry:teamsnap.teamsnap.api.LineupEntry, # Not implemented Yet
            teamsnap.models.Location: teamsnap.teamsnap.api.Location,
            teamsnap.models.Member: teamsnap.teamsnap.api.Member,
            teamsnap.models.Opponent: teamsnap.teamsnap.api.Opponent,
            teamsnap.models.Team: teamsnap.teamsnap.api.Team,
            # teamsnap.models.User:teamsnap.teamsnap.api.User # Not implemented yet
        }

        apiobject_to_teamsnapmodel = {v:k for k,v in teamsnapmodel_to_apiobject.items()}

        if isinstance(qs.first(), benchcoach.models.Team):
            # This situation requires special attention because opponents and teams share a table in BenchCoach
            if getattr(qs.first(), 'teamsnap_team', None):
                teamsnap_attribute_name = 'teamsnap_team'
            elif getattr(qs.first(), 'teamsnap_opponent', None):
                teamsnap_attribute_name = 'teamsnap_opponent'
        else:
            teamsnap_attribute_name = benchcoachmodel_to_teamsnapfield.get(type(qs.first()))

        ids = [getattr(i, teamsnap_attribute_name).id for i in qs]
        ApiObject = teamsnapmodel_to_apiobject.get(type(getattr(qs.first(), teamsnap_attribute_name)))
        api_responses = ApiObject.search(client=self.client, id=",".join(ids))
        r = []
        for api_response in api_responses:
            teamsnap_instance = apiobject_to_teamsnapmodel.get(type(api_response)).objects.get(id=api_response.data['id'])
            response = self._update_from_teamsnapdata(teamsnap_instance, api_response)
            response = self._update_teamsnapdb_to_benchcoachdb(teamsnap_instance, teamsnap_instance.benchcoach_object)
            r.append(response)
        return r

    def _sync_from_teamsnap(self, benchcoach_instance:BenchcoachModel)->BenchcoachModel:
        '''
        Syncs BenchCoach instance from TeamSnap. This function fetches the actual information from teamsnap, then
        hands it off to the self._update* functions.
        :param benchcoach_instance: instance to be synced
        :return: BenchCoach object that has been processed (but not necessarily changed) during sync.
        '''

        # I hate having this translation. What I really want is just a property for "teamsnap_object"
        # which would simplify all this, but I couldn't figure out how to implement in the
        # teamsnap model foreign key and "related_name" that didn't cause conflicts. I don't
        # think I need to be too much smarter to figure this out, but alas I am not smart enough.
        benchcoachmodel_to_teamsnapfield = {
            Availability:'teamsnap_availability',
            Player:'teamsnap_member',
            Team:'teamsnap_opponent',
            # Positioning:'teamsnap_lineupentry', # Not Implemented Yet, but will be 'teamsnap_lineupentry'
            Event:'teamsnap_event',
            Venue:'teamsnap_location'
        }

        teamsnapmodel_to_apiobject = {
            teamsnap.models.Availability: teamsnap.teamsnap.api.Availability,
            teamsnap.models.Event: teamsnap.teamsnap.api.Event,
            # teamsnap.models.LineupEntry:teamsnap.teamsnap.api.LineupEntry, # Not implemented Yet
            teamsnap.models.Location: teamsnap.teamsnap.api.Location,
            teamsnap.models.Member: teamsnap.teamsnap.api.Member,
            teamsnap.models.Opponent: teamsnap.teamsnap.api.Opponent,
            teamsnap.models.Team: teamsnap.teamsnap.api.Team,
            # teamsnap.models.User:teamsnap.teamsnap.api.User # Not implemented yet
        }

        if isinstance(benchcoach_instance, benchcoach.models.Team):
            # This situation requires special attention because opponents and teams share a table in BenchCoach
            teamsnap_instance =  getattr(benchcoach_instance, 'teamsnap_team', None)
            if not teamsnap_instance: teamsnap_instance = getattr(benchcoach_instance, 'teamsnap_opponent')
        else:
            teamsnap_instance = getattr(benchcoach_instance, benchcoachmodel_to_teamsnapfield.get(type(benchcoach_instance)))

        ApiObject = teamsnapmodel_to_apiobject.get(type(teamsnap_instance))
        api_response = ApiObject.get(self.client, teamsnap_instance.id)

        r = self._update_from_teamsnapdata(teamsnap_instance, api_response)
        r = self._update_teamsnapdb_to_benchcoachdb(teamsnap_instance, benchcoach_instance)
        return r

    def _update_from_teamsnapdata(self, teamsnap_instance:teamsnap.models.TeamsnapBaseModel, teamsnap_data: teamsnap.teamsnap.api.ApiObject) -> teamsnap.models.TeamsnapBaseModel:
        ''''''
        if isinstance(teamsnap_data, teamsnap.teamsnap.api.ApiObject):
            teamsnap_data = teamsnap_data.data
        else:
            raise TypeError
        if not teamsnap_data['type'] == teamsnap_instance.type:
            raise Exception()
        data_type = teamsnap_data['type']
        fields = ['id', 'created_at', 'updated_at']
        related_objects = {}
        if data_type in ['opponent', 'team', 'location']:
            fields += ['name']
        elif data_type == 'event':
            fields += [
                'label',
                'start_date',
                'formatted_title',
                'points_for_opponent',
                'points_for_team',
                'is_game',
                'game_type'
            ]
            if teamsnap_data.get('location_id'):
                related_objects['location'] = teamsnap.models.Location.objects.get(id=teamsnap_data['location_id'])
            if teamsnap_data.get('opponent_id'):
                related_objects['opponent'] = teamsnap.models.Opponent.objects.get(id=teamsnap_data['opponent_id'])
            pass

        elif data_type == 'member':
            fields += [
                'first_name',
                'last_name',
                'jersey_number',
                'is_non_player'
            ]

        elif data_type == 'availability':
            fields += ['status_code']
            related_objects['member'] = teamsnap.models.Member.objects.get(id=teamsnap_data['member_id'])
            related_objects['event'] = teamsnap.models.Event.objects.get(id=teamsnap_data['event_id'])

        else:
            raise ValueError

        if teamsnap_data.get('team_id'):
            related_objects['team'] = teamsnap.models.Team.objects.filter(id=teamsnap_data['team_id']).first()

        for field in fields:
            value = teamsnap_data.get(field)
            # if value is None:
            #     continue
            # else:
            setattr(teamsnap_instance,field,value)

        for related_object_name, related_object in related_objects.items():
            setattr(teamsnap_instance, related_object_name, related_object)

        teamsnap_instance.save()

        return teamsnap_instance

    def _update_teamsnapdb_to_benchcoachdb(self, teamsnap_instance, benchcoach_instance) -> List[Tuple[django.db.models.Model, bool]]:

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
                    pass

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
                raise Player.DoesNotExist

            if teamsnap_instance.event.benchcoach_object:
                d['event'] = teamsnap_instance.event.benchcoach_object
            elif not teamsnap_instance.event.benchcoach_object:
                raise Event.DoesNotExist

        else:
            raise ValueError

        for field, value in d.items():
            setattr(benchcoach_instance, field, value)

        benchcoach_instance.save()
        teamsnap_instance.benchcoach_object = benchcoach_instance
        teamsnap_instance.save()
        return benchcoach_instance

    def _find_counterpart(self, instance):
        '''
        find the counterpart BenchCoach object from the TeamSnap object.
        NOT CURRENTLY USED.
        :param instance:
        :return:
        '''
        instance_type = type(instance)
        counterpart_instance = None
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

        else:
            raise Exception()

        return counterpart_instance

    def _sync_qs (self, qs, direction):
        if direction == 'download':
            if qs.model not in self.models:
                raise TypeError(f"Sync engine does not sync {qs.model} models")

            r=[]
            r = self._bulk_sync_from_teamsnap(qs)

        elif direction == 'upload':
            raise NotImplementedError('Uploading not supported by this sync engine yet.')
        else:
            raise TypeError(f"Direction {direction} not supported. 'upload' or 'download' must be specified")

        return r

    def _sync_instance(self, instance, direction, data=None):
        r=[]
        if direction == 'download':
            r.append(self._sync_from_teamsnap(instance))

        elif direction == 'upload':
            raise NotImplementedError('Uploading not supported by this sync engine yet.')
        else:
            raise TypeError(f"Direction {direction} not supported. 'upload' or 'download' must be specified")

        return r

    def sync(self, qs: django.db.models.QuerySet = None, instance: benchcoach.models.BenchcoachModel = None,
             direction='download') -> List[Tuple[django.db.models.Model, bool]]:
        if not isinstance(qs, QuerySet) and not isinstance(instance, benchcoach.models.BenchcoachModel):
            raise TypeError(f"sync requires either a QuerySet or model instance to be provided")
        if qs and instance:
            raise TypeError(f"sync requires either a QuerySet or model instance to be provided, but not both")
        elif qs:
            r = self._sync_qs(qs, direction)
        elif instance:
            r = self._sync_instance(instance, direction)

        return r

    def import_items(self):
        '''
        Implementation of import items from the abstract base class AbstractSyncEngine.
        Imports objects from TeamSnap into BenchCoach, creating BenchCoach objects when necessary.
        It runs through all supported TeamSnap Objects every execution.
        NOTE: The number of availability objects causes this function to choke, so consider not updating
        those on import.
        :return:
        '''

        ['team', 'opponent', 'location', 'member', 'event', 'availability']

        # the common kwargs for searching the API. Most objects just need the client and currently managed team id.
        kwargs = {'client':self.client,'team_id': self.managed_teamsnap_team_id}

        # r is the result dictionary, the key is the name of the benchcoach object, and the value is the list of BenchCoach objects that
        # have been iterated (but not necessarily changed) during this import.
        r = {}

        # Walking through each TeamSnap object. There is a fair amount of repetition that could use clean-up.
        # ---team---
        r['team'] = []

        # Search API for objects belonging to currently managed team, and iterate
        for teamsnap_data in teamsnap.teamsnap.api.Team.search(client=self.client, id=self.managed_teamsnap_team_id):
            # check if TeamSnap ID already exists in the Teamsnap DB.
            if teamsnap.models.Team.objects.filter(id=teamsnap_data.data['id']):
                teamsnap_instance = teamsnap.models.Team.objects.filter(id=teamsnap_data.data['id']).first()
                # If it does, retrieve the BenchCoach instance attached.
                # It is enforced (by this import function) that every teamsnap instance has a related BenchCoach instance attached.
                # No other function can create TeamSnap instances (or create related BenchCoach instances from the TeamSnap service)
                benchcoach_instance = teamsnap_instance.benchcoach_object
            else:
                # Otherwise create TeamSnap instance
                teamsnap_instance = teamsnap.models.Team()
                # and create related BenchCoach instance
                benchcoach_instance = benchcoach.models.Team()
                # and attach it to the BenchCoach instance
                teamsnap_instance.benchcoach_object=benchcoach_instance
                benchcoach_instance.save()
            # Now, update the data from the API to the retrieved/created instances
            response = self._update_from_teamsnapdata(teamsnap_instance, teamsnap_data)
            teamsnap_instance.save()
            response = self._update_teamsnapdb_to_benchcoachdb(teamsnap_instance, benchcoach_instance)
            r['team'].append(response)

        # ---opponent---
        # See first object for additional comments on the steps followed.
        # Opponents from teamsnap go to the BenchCoach "Team" database.
        # Dependent on Team. These objects need to be available to attach as related objects or the functions
        # self._update_from teamsnapdata and self.update_teamsnapdb_to_benchcoachdb may fail.
        for teamsnap_data in teamsnap.teamsnap.api.Opponent.search(**kwargs):
            if teamsnap.models.Opponent.objects.filter(id=teamsnap_data.data['id']):
                teamsnap_instance = teamsnap.models.Opponent.objects.filter(id=teamsnap_data.data['id']).first()
                benchcoach_instance = teamsnap_instance.benchcoach_object
            else:
                teamsnap_instance = teamsnap.models.Opponent()
                benchcoach_instance = benchcoach.models.Team()
                teamsnap_instance.benchcoach_object = benchcoach_instance
                benchcoach_instance.save()
            response = self._update_from_teamsnapdata(teamsnap_instance, teamsnap_data)
            response = self._update_teamsnapdb_to_benchcoachdb(teamsnap_instance, benchcoach_instance)
            r['team'].append(response)

        # ---location---
        # See first object for additional comments on the steps followed.
        # Dependent on Team. These objects need to be available to attach as related objects or the functions
        # self._update_from teamsnapdata and self.update_teamsnapdb_to_benchcoachdb may fail.
        r['location'] = []
        for teamsnap_data in teamsnap.teamsnap.api.Location.search(**kwargs):
            if teamsnap.models.Location.objects.filter(id=teamsnap_data.data['id']):
                teamsnap_instance = teamsnap.models.Location.objects.filter(id=teamsnap_data.data['id']).first()
                benchcoach_instance = teamsnap_instance.benchcoach_object
            else:
                teamsnap_instance = teamsnap.models.Location()
                benchcoach_instance = benchcoach.models.Venue()
                teamsnap_instance.benchcoach_object = benchcoach_instance
                benchcoach_instance.save()

            response = self._update_from_teamsnapdata(teamsnap_instance, teamsnap_data)
            response = self._update_teamsnapdb_to_benchcoachdb(teamsnap_instance, benchcoach_instance)
            r['location'].append(response)

        # ---member---
        # See first object for additional comments on the steps followed.
        # Dependent on Team. These objects need to be available to attach as related objects or the functions
        # self._update_from teamsnapdata and self.update_teamsnapdb_to_benchcoachdb may fail.
        r['member'] = []
        # Search API for members to import. Note: Non players are not included in sync.
        for teamsnap_data in teamsnap.teamsnap.api.Member.search(**kwargs,
                                                                 is_non_player = False
                                                                 ):
            if teamsnap_data.data['is_non_player'] == True:
                continue
            if teamsnap.models.Member.objects.filter(id=teamsnap_data.data['id']):
                teamsnap_instance = teamsnap.models.Member.objects.filter(id=teamsnap_data.data['id']).first()
                benchcoach_instance = teamsnap_instance.benchcoach_object
            else:
                teamsnap_instance = teamsnap.models.Member()
                benchcoach_instance = benchcoach.models.Player()
                teamsnap_instance.benchcoach_object = benchcoach_instance
                benchcoach_instance.save()

            response = self._update_from_teamsnapdata(teamsnap_instance, teamsnap_data)
            response = self._update_teamsnapdb_to_benchcoachdb(teamsnap_instance, benchcoach_instance)
            r['member'].append(response)

        # ---event---
        # See first object for additional comments on the steps followed.
        # Dependent on Team, Opponent, Location. These objects need to be available to attach as related objects or the functions
        # self._update_from teamsnapdata and self.update_teamsnapdb_to_benchcoachdb may fail.
        r['event'] = []
        for teamsnap_data in teamsnap.teamsnap.api.Event.search(**kwargs):
            if teamsnap.models.Event.objects.filter(id=teamsnap_data.data['id']):
                teamsnap_instance = teamsnap.models.Event.objects.filter(id=teamsnap_data.data['id']).first()
                benchcoach_instance = teamsnap_instance.benchcoach_object
            else:
                teamsnap_instance = teamsnap.models.Event()
                benchcoach_instance = benchcoach.models.Event()
                teamsnap_instance.benchcoach_object = benchcoach_instance
                benchcoach_instance.save()

            response = self._update_from_teamsnapdata(teamsnap_instance, teamsnap_data)
            response = self._update_teamsnapdb_to_benchcoachdb(teamsnap_instance, benchcoach_instance)
            r['event'].append(response)

        # ---availability---
        # See first object for additional comments on the steps followed.
        # Availability was  a bit tricky to implement, because there are "not null" contstraints for the Availability object in Bench Coach
        # Ideally, there probably should be more "not null" constraints on more of the BenchCoach models, so a generalized function should
        # look more like this than the ones above.
        # Dependent on Team, Member, Event. These objects need to be available to attach as related objects or the functions
        # self._update_from teamsnapdata and self.update_teamsnapdb_to_benchcoachdb may fail.
        #TODO this import is wonky and causes errors on servers. maybe skip this import, or do it in chunks?
        r['availability'] = []

        # Search API for members to import. Note: Non players are not included in sync.
        player_ids = [member.id for member in teamsnap.models.Member.objects.filter(is_non_player=False)]
        for teamsnap_data in teamsnap.teamsnap.api.Availability.search(**kwargs,
                                                                       member_id=",".join(player_ids)
                                                                       ):
            if teamsnap.models.Availability.objects.filter(id=teamsnap_data.data['id']):
                teamsnap_instance = teamsnap.models.Availability.objects.filter(id=teamsnap_data.data['id']).first()
                benchcoach_instance = teamsnap_instance.benchcoach_object
            else:
                teamsnap_instance = teamsnap.models.Availability()
                event_instance = benchcoach.models.Event.objects.get(teamsnap_event__id=teamsnap_data.data['event_id'])
                player_instance = benchcoach.models.Player.objects.get(teamsnap_member__id=teamsnap_data.data['member_id'])
                benchcoach_instance = benchcoach.models.Availability(event=event_instance, player=player_instance)
                benchcoach_instance.save()
                teamsnap_instance.benchcoach_object_id = benchcoach_instance.id
            response = self._update_from_teamsnapdata(teamsnap_instance, teamsnap_data)
            response = self._update_teamsnapdb_to_benchcoachdb(teamsnap_instance, benchcoach_instance)
            r['availability'].append(response)

        return r