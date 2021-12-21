import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "benchcoachproject.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "benchcoachproject.settings"
import django
django.setup()

from teamsnap.teamsnap.api import TeamSnap
import teamsnap.teamsnap.api
from teamsnap.models import User, Member, Team, Event, Location, Availability, Opponent, TeamsnapBaseModel
from typing import List, Type, Tuple
from benchcoachproject.models import Profile as BenchcoachUser
import benchcoach.models
from django.db import models
import pytz

def update_teamsnapbasemodel_from_teamsnap(
        TeamsnapModel: Type[TeamsnapBaseModel],
        teamsnap_client: teamsnap.teamsnap.api.TeamSnap,
        fields: List[str]= ['created_at', 'updated_at'],
        additional_fields: List[str] = [],
        related_fields: List[Tuple[str, Type[TeamsnapBaseModel]]] = [],
        create = True,
        create_related = True,
        **teamsnap_search_kwargs
):
    api_response_objects = TeamsnapModel.ApiObject.search(
        client=teamsnap_client, **teamsnap_search_kwargs
    )

    r = []

    for response_object in api_response_objects:
        d = {k:response_object.data[k] for k in fields}
        d.update({k:response_object.data[k] for k in additional_fields})

        for related_field_name, RelatedTeamSnapModel in related_fields:
            related_field_name = f"{related_field_name}_id"
            filter_criteria = {related_field_name:response_object.data[related_field_name]}
            if related_field_name == "team_id" and RelatedTeamSnapModel.__name__ == "Team":
                filter_criteria = {'id':response_object.data[related_field_name]}
            related_teamsnap_object = RelatedTeamSnapModel.objects.filter(**filter_criteria).first()
            if related_teamsnap_object:
                d[related_field_name] = related_teamsnap_object
            elif not related_teamsnap_object and create_related:
                related_teamsnap_object = RelatedTeamSnapModel(**{related_field_name:response_object.data[related_field_name]})
                related_teamsnap_object.save()
            elif not related_teamsnap_object and not create_related:
                raise RelatedTeamSnapModel.DoesNotExist

        teamsnap_object = TeamsnapModel.objects.filter(id=response_object.data['id'])
        if teamsnap_object:
            teamsnap_object.update(**d)
            created = False
            r.append((teamsnap_object.first(), created))
        elif not teamsnap_object and create:
            new_teamsnap_object = TeamsnapModel(**d)  # create new benchcoach object
            new_teamsnap_object.save()
            created = True
            r.append((new_teamsnap_object, created))
        elif not teamsnap_object and not create:
            raise TeamsnapModel.DoesNotExist

    return r

def update_events(
        teamsnap_client: teamsnap.teamsnap.api.TeamSnap,
        create: bool = True,
        create_related: bool = False,
        **teamsnap_search_kwargs
):
    r = update_teamsnapbasemodel_from_teamsnap(
        TeamsnapModel= Event,
        teamsnap_client= teamsnap_client,
        additional_fields=['label', 'start_date', 'formatted_title', 'points_for_opponent', 'points_for_team', 'is_game', 'game_type'],
        related_fields=[('location', Location), ('opponent', Opponent), ('team', Team)],
        create=create,
        create_related=create_related,
        **teamsnap_search_kwargs
    )

    return r

def update_opponents(
        teamsnap_client: teamsnap.teamsnap.api.TeamSnap,
        create: bool = True,
        create_related: bool = False,
        **teamsnap_search_kwargs
):
    r = update_teamsnapbasemodel_from_teamsnap(
        TeamsnapModel= Opponent,
        teamsnap_client= teamsnap_client,
        additional_fields=['name'],
        related_fields=[('team', Team)],
        create=create,
        create_related=create_related,
        **teamsnap_search_kwargs
    )

    return r

def update_teams(
        teamsnap_client: teamsnap.teamsnap.api.TeamSnap,
        create: bool = True,
        create_related: bool = False,
        **teamsnap_search_kwargs
):
    r = update_teamsnapbasemodel_from_teamsnap(
        TeamsnapModel=Team,
        teamsnap_client=teamsnap_client,
        additional_fields=['name'],
        create=create,
        create_related=create_related,
        **teamsnap_search_kwargs
    )


def update_locations(
        teamsnap_client: teamsnap.teamsnap.api.TeamSnap,
        create: bool = True,
        create_related: bool = False,
        **teamsnap_search_kwargs
):
    r = update_teamsnapbasemodel_from_teamsnap(
        TeamsnapModel=Location,
        teamsnap_client=teamsnap_client,
        additional_fields=['name'],
        related_fields=[('team', Team)],
        create=create,
        create_related=create_related,
        **teamsnap_search_kwargs
    )

def update_availabilities(teamsnap_client: teamsnap.teamsnap.api.TeamSnap,
        create: bool = True,
        create_related: bool = False,
        **teamsnap_search_kwargs
):
    r = update_teamsnapbasemodel_from_teamsnap(
        TeamsnapModel= Availability,
        teamsnap_client= teamsnap_client,
        related_fields=[('event', Event), ('member', Member), ('team', Team)],
        create=create,
        create_related=create_related,
        **teamsnap_search_kwargs
    )

def import_teamsnap():
    user = BenchcoachUser.objects.get(id=1)
    TOKEN = user.teamsnap_access_token
    USER_ID = user.teamsnap_user.id
    TEAM_ID = user.teamsnapsettings.managed_team.id
    CLIENT = TeamSnap(token=TOKEN)

    l = []
    for team in Opponent.objects.filter(managed_by_team_id=TEAM_ID):
        l += update_opponent(team, create_benchcoach_object=True, create_related=True)

    for team in Team.objects.filter(id=TEAM_ID):
        l += update_team(team, create_benchcoach_object=True, create_related=True)

    for location in Location.objects.filter(managed_by_team_id=TEAM_ID):
        l += update_location(location, create_benchcoach_object=True, create_related=True)

    for member in Member.objects.filter(managed_by_team_id=TEAM_ID, is_non_player=False):
        l += update_member(member, create_benchcoach_object= True, create_related=True)

    for event in Event.objects.filter(managed_by_team_id=TEAM_ID):
        l += update_event(event, create_benchcoach_object=True, create_related=True)

    for availability in Availability.objects.filter(managed_by_team_id=TEAM_ID):
        l += update_availability(availability, create_benchcoach_object=True, create_related=True)

    pass
    # l += update_teams(CLIENT, team_id=TEAM_ID)
    # l += update_members(CLIENT, team_id=TEAM_ID)
    # l += update_locations(CLIENT, team_id=TEAM_ID)
    # l += update_events(CLIENT, team_id=TEAM_ID)
    # l += update_availabilities(CLIENT, team_id=TEAM_ID)

if __name__ == "__main__":

    TOKEN = BenchcoachUser.objects.get(id=1).teamsnap_access_token
    USER_ID = BenchcoachUser.objects.get(id=1).teamsnap_user_id
    TEAM_ID = BenchcoachUser.objects.get(id=1).teamsnapsettings.managed_team_id
    CLIENT = TeamSnap(token=TOKEN)
    for Obj in [User]:
        a = Obj.ApiObject.search(CLIENT, id=USER_ID)
        for _a in a:
            obj, created = Obj.update_or_create_from_teamsnap_api(_a.data)

    for Obj in [Event, Availability, Location, Member, Opponent, Team]:
        a = Obj.ApiObject.search(CLIENT, team_id=TEAM_ID)
        for _a in a:
            obj, created = Obj.update_or_create_from_teamsnap_api(_a.data)
    # update_opponents(CLIENT, team_id=TEAM_ID)
    # update_events(CLIENT, team_id=TEAM_ID)