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
import benchcoach.models
from django.db import models
import pytz

def update_teamsnap_object(d, teamsnap_object: TeamsnapBaseModel, benchcoach_model: models.Model ,create_benchcoach_object: bool = True, create_related: bool = False):
    ''' Function to update from a teamsnap object to Benchcoach object. This method is a simple method when there are no related objects

    :param d: The information to update.
    :param teamsnap_object: The teamsnap object from which to update.
    :param create_benchcoach_object: If true, will create the benchcoach object if it doesn't exist
    :param create_related: This is here for decoration only. It doesn't do anything.
    :return: a list of tuples in the form (obj, did_create) for created or modified objects.
    '''

    r = []

    if teamsnap_object.benchcoach_object:
        #TODO I'm not sure this does anything. need to make sure.
        benchcoach_object = benchcoach_model.objects.filter(id=teamsnap_object.benchcoach_object.id)
        benchcoach_object.update(**d)
        created = False
        r.append((benchcoach_object.first(), created))
    elif not teamsnap_object.benchcoach_object and create_benchcoach_object:
        benchcoach_object = benchcoach_model(**d)  # create new benchcoach object
        teamsnap_object.benchcoach_object = benchcoach_object
        benchcoach_object.save()
        teamsnap_object.save()
        created = True
        r.append((benchcoach_object, created))
    elif not teamsnap_object.benchcoach_object:
        raise benchcoach.models.Team.DoesNotExist

    return r

def update_event(event: Event, create_benchcoach_object: bool = True, create_related=False):
    benchcoach_model = benchcoach.models.Event

    d = {
        'start': event.start_date,
    }

    r = []

    if event.team:
        if event.team.benchcoach_object:
            if event.game_type == "Home":
                d['home_team'] = event.team.benchcoach_object
            elif event.game_type == "Away":
                d['away_team'] = event.team.benchcoach_object
        elif not event.team.benchcoach_object and create_related:
            # create team object
            # update_opponent
            # r.append
            pass
        elif not event.team.benchcoach_object:
            raise benchcoach.models.Team.DoesNotExist

    if event.opponent:
        if event.opponent.benchcoach_object:
            if event.game_type == 'Home':
                d['away_team'] = event.opponent.benchcoach_object
            elif event.game_type == 'Away':
                d['home_team'] = event.opponent.benchcoach_object
        elif not event.opponent.benchcoach_object and create_related:
            # Create opponent object
            # update_opponent()
            # r.append
            pass
        elif not event.opponent.benchcoach_object:
            raise benchcoach.models.Team.DoesNotExist

    if event.location:
        if event.location.benchcoach_object:
            if event.location:
                d['venue'] = event.location.benchcoach_object
        elif not event.location.benchcoach_object and create_related:
            # Need to account for if no loacation assigned to teamsnap object.
            # create team object
            # update_opponent
            # r.append
            pass
        elif not event.location.benchcoach_object:
            raise benchcoach.models.Venue.DoesNotExist

    r += update_teamsnap_object(d, teamsnap_object=event, benchcoach_model=benchcoach_model, create_benchcoach_object=create_benchcoach_object)

    return r

def update_opponent(opponent: Opponent, create_benchcoach_object: bool = True, create_related: bool = False):
    benchcoach_model = benchcoach.models.Team
    d = {
        'name': opponent.name,
    }

    r = update_teamsnap_object(d, teamsnap_object=opponent, benchcoach_model=benchcoach_model, create_benchcoach_object= create_benchcoach_object, create_related = create_related)

    return r

def update_team(teamsnap_object: Team, create_benchcoach_object: bool = True, create_related: bool = False):
    benchcoach_model = benchcoach.models.Team
    d = {
        'name': teamsnap_object.name,
    }

    r = update_teamsnap_object(d, teamsnap_object=teamsnap_object, benchcoach_model=benchcoach_model, create_benchcoach_object=create_benchcoach_object,
                               create_related=create_related)

    return r

def update_location(teamsnap_object: Location, create_benchcoach_object: bool = True, create_related: bool = False):
    benchcoach_model = benchcoach.models.Venue
    d = {
        'name': teamsnap_object.name,
    }

    r = update_teamsnap_object(d, teamsnap_object=teamsnap_object, benchcoach_model=benchcoach_model, create_benchcoach_object=create_benchcoach_object,
                               create_related=create_related)

    return r

def update_member(teamsnap_object: Member, create_benchcoach_object: bool = True, create_related: bool = False):
    benchcoach_model = benchcoach.models.Player
    d = {
            'first_name': teamsnap_object.first_name,
            'last_name': teamsnap_object.last_name,
            'jersey_number': teamsnap_object.jersey_number,
        }

    r = update_teamsnap_object(d, teamsnap_object=teamsnap_object, benchcoach_model=benchcoach_model, create_benchcoach_object=create_benchcoach_object,
                               create_related=create_related)

    return r

def update_availability(availability: Availability, create_benchcoach_object: bool = True, create_related: bool = False):
    benchcoach_model = benchcoach.models.Availability
    translation = {
        Availability.YES: benchcoach.models.Availability.YES,
        Availability.NO: benchcoach.models.Availability.NO,
        Availability.MAYBE: benchcoach.models.Availability.MAYBE
    }

    d = {
        'available': translation.get(availability.status_code, benchcoach.models.Availability.UNKNOWN),
        'player': availability.member.benchcoach_object,
        'event': availability.event.benchcoach_object
    }

    r = []

    if availability.member.benchcoach_object:
        d['player'] = availability.member.benchcoach_object
    elif not availability.member.benchcoach_object and create_related:
        r += update_member(availability.member, create_benchcoach_object = True)
        d['player'] = availability.member.benchcoach_object
    elif not availability.member.benchcoach_object and not create_related:
        raise benchcoach.models.Availability.DoesNotExist

    if availability.event.benchcoach_object:
        d['event'] = availability.event.benchcoach_object
    elif not availability.event.benchcoach_object and create_related:
        r += update_event(availability.member, create_benchcoach_object = True)
        d['event'] = availability.event.benchcoach_object
    elif not availability.event.benchcoach_object and not create_related:
        raise benchcoach.models.Event.DoesNotExist

    r += update_teamsnap_object(d, teamsnap_object=availability, benchcoach_model=benchcoach_model, create_benchcoach_object=create_benchcoach_object,
                               create_related=create_related)

    return r


def import_teamsnap():
    user = BenchcoachUser.objects.get(id=1)
    TOKEN = user.teamsnap_access_token
    USER_ID = user.teamsnap_user.id
    TEAM_ID = user.teamsnapsettings.managed_team.id
    CLIENT = TeamSnap(token=TOKEN)

    l = []
    for team in Opponent.objects.filter(team_id=TEAM_ID):
        l += update_opponent(team, create_benchcoach_object=True, create_related=True)

    for team in Team.objects.filter(id=TEAM_ID):
        l += update_team(team, create_benchcoach_object=True, create_related=True)

    for location in Location.objects.filter(team_id=TEAM_ID):
        l += update_location(location, create_benchcoach_object=True, create_related=True)

    for member in Member.objects.filter(team_id=TEAM_ID, is_non_player=False):
        l += update_member(member, create_benchcoach_object= True, create_related=True)

    for event in Event.objects.filter(team_id=TEAM_ID):
        l += update_event(event, create_benchcoach_object=True, create_related=True)

    for availability in Availability.objects.filter(team_id=TEAM_ID):
        l += update_availability(availability, create_benchcoach_object=True, create_related=True)

    pass
    # l += update_teams(CLIENT, team_id=TEAM_ID)
    # l += update_members(CLIENT, team_id=TEAM_ID)
    # l += update_locations(CLIENT, team_id=TEAM_ID)
    # l += update_events(CLIENT, team_id=TEAM_ID)
    # l += update_availabilities(CLIENT, team_id=TEAM_ID)

if __name__ == "__main__":
    import_teamsnap()