from django.shortcuts import render, redirect

from .models import User, Member, Team, Event, Location, LineupEntry, Opponent, Availability
from django.http import HttpResponse
import benchcoach.models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils.teamsnap_sync_engine import TeamsnapSyncEngine

def edit_event(request, id):
    '''
    redirect to teamsnap.com page for editing of event.
    :param request:
    :param id:
    :return:
    '''
    event = Event.objects.get(id = id)
    return redirect(event.edit_url)

@login_required()
def home(request):
    current_benchcoach_user = request.user
    current_teamsnap_user = request.user.profile.teamsnap_user
    current_teamsnap_team = request.user.profile.teamsnapsettings.managed_team
    teamsnap_objects = {}
    for teamsnap_obj, benchcoach_object in [
        (Availability, benchcoach.models.Availability),
        (Event, benchcoach.models.Event),
        (LineupEntry, benchcoach.models.Positioning),
        (Location, benchcoach.models.Venue),
        (Member, benchcoach.models.Player),
        (Opponent, benchcoach.models.Team),
        (Team, benchcoach.models.Team),
        # (User, {'name':})
    ]:
        teamsnap_objects[teamsnap_obj.__name__.lower()] = {}
        teamsnap_objects[teamsnap_obj.__name__.lower()]['object_count'] = teamsnap_obj.objects.count()
        if benchcoach_object:
            teamsnap_objects[teamsnap_obj.__name__.lower()]['counterpart'] = {'name':benchcoach_object.__name__.lower()}
            teamsnap_objects[teamsnap_obj.__name__.lower()]['counterpart']['object_count'] = benchcoach_object.objects.count()

    context= {
        'benchcoach_user': current_benchcoach_user,
        'teamsnap_user': current_teamsnap_user,
        'teamsnap_team':current_teamsnap_team,
        'teamsnap_objects': teamsnap_objects
    }
    return render(request, 'teamsnap/home.html', context)

@login_required()
def sync_from_teamsnap(request, object_name=None, object_id=None):
    if request.POST:
        next = request.POST.get('next')
        object_name = request.POST.get('object_name')
        object_id = request.POST.get('object_id')

        Object = {
            obj.__name__.lower(): obj
            for obj in
            [Availability, Event, LineupEntry, Location, Member, Opponent, Team, User]
        }.get(object_name)

        TEAM_ID = request.user.profile.teamsnapsettings.managed_team.id
        TOKEN = request.user.profile.teamsnap_access_token

        sync_engine = TeamsnapSyncEngine(teamsnap_token=TOKEN, managed_team_teamsnap_id=TEAM_ID)
        r = {}

        r[object_name]=[]

        if object_name == 'team':
            if object_id:
                r[object_name] = sync_engine.sync(qs=benchcoach.models.Team.objects.filter(id=object_id))
            else:
                r[object_name] = sync_engine.sync(qs=benchcoach.models.Team.objects.all())

        if object_name == 'venue':
            if object_id:
                r[object_name] = sync_engine.sync(qs=benchcoach.models.Venue.objects.filter(id=object_id))
            else:
                r[object_name] = sync_engine.sync(qs=benchcoach.models.Venue.objects.all())

        if object_name == 'player':
            if object_id:
                r[object_name] = sync_engine.sync(qs=benchcoach.models.Player.objects.filter(id=object_id))
            else:
                r[object_name] = sync_engine.sync(qs=benchcoach.models.Player.objects.all())

        if object_name == 'event':
            if object_id:
                r[object_name] = sync_engine.sync(qs=benchcoach.models.Event.objects.filter(id=object_id))
                r['availability'] = sync_engine.sync(qs=benchcoach.models.Event.objects.get(id=object_id).availability_set.all())
            else:
                r[object_name] = sync_engine.sync(qs=benchcoach.models.Event.objects.all())

        if object_name == 'availability':
            r[object_name] = []
            if object_id:
                r[object_name] += sync_engine.sync(qs=benchcoach.models.Availability.objects.filter(id=object_id))
            else:
                for event in benchcoach.models.Player.objects.all():
                    r[object_name] += sync_engine.sync(qs=event.availability_set.all())

        for object_name, results in r.items():
            if len(results) == 0:
                messages.error(request, f"Error! No {object_name} objects updated")
            else:
                messages.success(request, f"Success! {len(results)} {object_name} objects updated.")

        return redirect(next)
    else:
        return HttpResponse(404)


def import_teamsnap(request):
    TEAM_ID = request.user.profile.teamsnapsettings.managed_team.id
    TOKEN = request.user.profile.teamsnap_access_token

    sync_engine = TeamsnapSyncEngine(teamsnap_token=TOKEN, managed_team_teamsnap_id=TEAM_ID)
    r = sync_engine.import_items()

    for object_name, results in r.items():
        if len(results) == 0:
            messages.error(request, f"Error! No {object_name} objects created or updated")
        else:
            messages.success(request, f"Success! {len(results)} {object_name} objects imported")

    return redirect('teamsnap home')



