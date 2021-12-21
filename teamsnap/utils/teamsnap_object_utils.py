import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "benchcoachproject.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "benchcoachproject.settings"
import django
django.setup()

from teamsnap.teamsnap.api import TeamSnap
import teamsnap.teamsnap.api
from teamsnap.models import User, Member, Team, Event, Location, Availability, Opponent, TeamsnapBaseModel
from typing import List
from benchcoachproject.models import Profile as BenchcoachUser


def update_object_from_teamsnap(
        TeamsnapApiObject: teamsnap.teamsnap.api.ApiObject,
        TeamsnapDbModelClass: teamsnap.models.TeamsnapBaseModel,
        TeamsnapClient: teamsnap.teamsnap.api.TeamSnap,
        teamsnap_search_kwargs: dict,
        fetching_keys: List[tuple] = ['id'],
        default_keys: List[tuple] = ['name'],
        related_objects: List[tuple] = []
):

    """
    Import or Update database objects from TeamSnap API. Currently this depends on being run in a particular order when the database is empty.

    additional_fetching_keys (key,) or (api_key, db_field_name) or (api_key, db_field_name, callable)
    Additional kwargs used to fetch an object from the database. ('id', 'teamsnap_id') are already included
    Callable will be run with the retrieved value as an argument. Example uses for this callable are to sanitize the value
    such as for a date, or to retrieve another database object

    additional_default_keys
    Additional Keys used to update the object (key,) or (api_key, db_field_name) or (api_key, db_field_name, callable)
    ('name',) is already included
    Callable will be run with the retrieved value as an argument. Example uses for this callable are to sanitize the value
    such as for a date, or to retrieve another database object

    :rtype: object
    """
    api_response = TeamsnapApiObject.search(client=TeamsnapClient, **teamsnap_search_kwargs)

    # This routine allows, for convenience, simplers tuples in which the additional detail is not needed
    # for example [('key', 'key', None)] can be passed as ['key'] if the TeamsnapApi key is the same as the TeamsnapDb field/key
    # and doesn't need to be sanitized
    for d in [fetching_keys, fetching_keys, default_keys]:
        for i, key in enumerate(d):
            if isinstance(key, tuple):
                if len(key) == 1:
                    d[i] = (key[0], key[0], None)
                if len(key) == 2:
                    d[i] = (key[0], key[1], None)
            elif isinstance(key, str):
                d[i] = (key, key, None)

    r = []
    for related_object in related_objects:
        pass

    for data in [items.data for items in api_response]:
        kwargs, defaults = {}, {}
        for api_key, db_field_name, callable_function in fetching_keys:
            if api_key in data.keys():
                kwargs[db_field_name] = callable_function(data[api_key]) if callable_function else data[api_key]
        for api_key, db_field_name, callable_function in default_keys:
            if api_key in data.keys():
                defaults[db_field_name] = callable_function(data[api_key]) if callable_function else data[api_key]
        defaults ={k:v for k,v in defaults.items() if v is not None}
        obj, created = TeamsnapDbModelClass.objects.update_or_create(**kwargs, defaults=defaults)
        r.append((obj,created))
    return r

def update_locations (client, **kwargs):
    return update_object_from_teamsnap(
        teamsnap.teamsnap.api.Location,
        Location,
        TeamsnapClient=client,
        teamsnap_search_kwargs=kwargs,
        default_keys=[
            'name', 'created_at', 'updated_at',
            ('team_id', 'managed_by_team_id')
        ]
    )

def update_teams (client, **kwargs):
    teams = update_object_from_teamsnap(
        teamsnap.teamsnap.api.Team,
        Team,
        TeamsnapClient=client,
        teamsnap_search_kwargs=kwargs,
        default_keys=[
            'name', 'created_at', 'updated_at'
        ],
        related_objects = [
            ('team_id', 'managed_by_team_id')
        ]
    )
    opponents = update_object_from_teamsnap(
        teamsnap.teamsnap.api.Opponent,
        Opponent,
        TeamsnapClient=client,
        teamsnap_search_kwargs=kwargs,
        default_keys= [
            'name', 'created_at', 'updated_at',
            ('team_id', 'managed_by_team_id')
        ]
    )
    return teams + opponents

def update_members (client, **kwargs):
    return update_object_from_teamsnap(
        TeamsnapApiObject=teamsnap.teamsnap.api.Member,
        TeamsnapDbModelClass=Member,
        TeamsnapClient=client,
        teamsnap_search_kwargs=kwargs,
        default_keys=['first_name','last_name','jersey_number','is_non_player', 'created_at', 'updated_at',
            ('team_id', 'managed_by_team_id'),
        ]
    )
    pass

def update_availabilities(client, **kwargs):
    return update_object_from_teamsnap(
        TeamsnapApiObject=teamsnap.teamsnap.api.Availability,
        TeamsnapDbModelClass=Availability,
        TeamsnapClient=client,
        teamsnap_search_kwargs=kwargs,
        default_keys=[ 'status_code',
                       'member_id',
                       'event_id',
                       'created_at',
                       'updated_at',
                       ('team_id', 'managed_by_team_id')
                       ]
    )

def update_events(client, **kwargs):
    return update_object_from_teamsnap(
        TeamsnapApiObject=teamsnap.teamsnap.api.Event,
        TeamsnapDbModelClass=Event,
        TeamsnapClient=client,
        teamsnap_search_kwargs=kwargs,
        default_keys=['formatted_title','label','points_for_opponent','points_for_team','is_game','opponent_id','location_id',
            'start_date', 'created_at', 'updated_at', 'game_type',
            ('team_id', 'managed_by_team_id')
        ]
    )

def update_users(client, **kwargs):
    return update_object_from_teamsnap(
        TeamsnapApiObject=teamsnap.teamsnap.api.User,
        TeamsnapDbModelClass=User,
        TeamsnapClient=client,
        teamsnap_search_kwargs=kwargs,
        default_keys=['first_name', 'last_name', 'email', 'created_at', 'updated_at',]
    )

if __name__ == "__main__":
    TOKEN = BenchcoachUser.objects.get(id=1).teamsnap_access_token
    USER_ID = BenchcoachUser.objects.get(id=1).teamsnap_user_id
    TEAM_ID = BenchcoachUser.objects.get(id=1).teamsnapsettings.managed_team_id
    CLIENT = TeamSnap(token=TOKEN)
    # update_users(CLIENT, id=USER_ID)
    update_teams(CLIENT, team_id=TEAM_ID)