from django.shortcuts import render, redirect

from .teamsnap.api import Event as TsApiEvent
from .teamsnap.api import TeamSnap
from .models import User, Member, Team, Event, Location, LineupEntry, Opponent, Availability
from lib.views import BenchcoachListView
from .forms import EventForm, MemberForm, OpponentForm, TeamForm, LocationForm
from django.urls import reverse
from django.db.models import Case, When
from django.views import View
from django.http import HttpResponse
import benchcoachproject.models
import benchcoach.models
from django.http import JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string
from .utils.import_teamsnap import update_team, update_event, update_member, update_location, update_opponent, update_availability, update_teamsnap_object
from django.forms import modelformset_factory
import django.db.models
from django.contrib.auth.decorators import login_required



def queryset_from_ids(Model, id_list):
    #https://stackoverflow.com/questions/4916851/django-get-a-queryset-from-array-of-ids-in-specific-order
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(id_list)])
    queryset = Model.objects.filter(pk__in=id_list).order_by(preserved)
    return queryset

def edit_event(request, id):
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

class TeamsnapObjTableView(View):
    Model = None
    Form = None
    template = 'teamsnap/table.html'
    options = {
        'event': (Event, EventForm),
        'location': (Location, LocationForm),
        'member': (Member, MemberForm),
        'opponent': (Opponent, OpponentForm),
        'team': (Team, TeamForm)
    }

    def post(self, request, object):
        self.Model, self.Form = self.options[object]
        self.Formset = modelformset_factory(
            model=self.Model,
            form=self.Form,
            extra=0
        )
        formset = self.Formset(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return HttpResponse(200)
        else:
            return HttpResponse(422)
            pass

    def get(self, request, object):
        self.Model, self.Form = self.options[object]
        self.Formset = modelformset_factory(
            model=self.Model,
            form=self.Form,
            extra=0
        )
        qs = self.Model.objects.all()
        formset = self.Formset(queryset=qs)
        return render(request, self.template, context={'formset': formset})

@login_required()
def sync(request):
    object_name = request.POST.get('object_name')
    object_id = request.POST.get('object_id')
    if request.POST and request.POST.get('object_name') and request.POST.get('object_id'):
        TOKEN = request.user.profile.teamsnap_access_token
        USER_ID = request.user.profile.teamsnap_user.id
        TEAM_ID = request.user.profile.teamsnapsettings.managed_team.id
        CLIENT = TeamSnap(token=TOKEN)

        object_name = request.POST.get('object_name')
        object_id = request.POST.get('object_id')
        Object = {
            obj.__name__.lower(): obj
            for obj in
            [Availability, Event, LineupEntry, Location, Member, Opponent, Team]
        }.get(object_name)

        r={}
        r[Object.__name__.lower()] = []
        a = Object.ApiObject.search(CLIENT, id=object_id)
        if a and len(a) == 1:
            obj, created = Object.update_or_create_from_teamsnap_api(a[0].data)
            r[Object.__name__.lower()].append((obj, created))

        for object_name, results in r.items():
            if len(results) == 0:
                messages.error(request, f"Error! No {object_name} objects created or updated")
            else:
                result = [created for obj, created in results]
                messages.success(request,
                                 f"Success! {sum(result)} {object_name} objects created, {len(result) - sum(result)} {object_name} objects updated.")

        return redirect(request.POST.get('next'))

    return HttpResponse('404')


@login_required()
def update_teamsnapdb_from_teamsnapapi(request, object_name, object_id=None):
    TOKEN = request.user.profile.teamsnap_access_token
    USER_ID = request.user.profile.teamsnap_user.id
    TEAM_ID = request.user.profile.teamsnapsettings.managed_team.id
    CLIENT = TeamSnap(token=TOKEN)

    Object = {
        obj.__name__.lower():obj
        for obj in
        [Availability, Event, LineupEntry, Location, Member, Opponent, Team, User]
    }.get(object_name)

    r = {}

    for Obj in [Object]:
        r[Obj.__name__.lower()] = []
        if not object_id:
            a = Obj.ApiObject.search(CLIENT, team_id=TEAM_ID)
            for _a in a:
                obj, created = Obj.update_or_create_from_teamsnap_api(_a.data)
                r[Obj.__name__.lower()].append((obj, created))
        else:
            a = Obj.ApiObject.search(CLIENT, id=object_id)[0]
            obj, created = Obj.update_or_create_from_teamsnap_api(a.data)
            r[Obj.__name__.lower()].append((obj, created))

    for object_name, results in r.items():
        if len(results) == 0:
            messages.error(request, f"Error! No {object_name} objects created or updated")
        else:
            result = [created for obj, created in results]
            messages.success(request,
                             f"Success! {sum(result)} {object_name} objects created, {len(result) - sum(result)} {object_name} objects updated.")

    return redirect('teamsnap home')

@login_required()
def send_to_benchcoach(request, object_name):
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
        r[object_name] = sync_engine.sync(qs=benchcoach.models.Team.objects.all())

    if object_name == 'venue':
        r[object_name] = sync_engine.sync(qs=benchcoach.models.Venue.objects.all())
        pass

    if object_name == 'player':
        r[object_name] = sync_engine.sync(qs=benchcoach.models.Player.objects.all())

    if object_name == 'event':
        r[object_name] = sync_engine.sync(qs=benchcoach.models.Event.objects.all())
        pass

    if object_name == 'availability':
        r[object_name] = []
        for event in benchcoach.models.Player.objects.all():
            r[object_name] += sync_engine.sync(qs=event.availability_set.all())

    for object_name, results in r.items():
        if len(results) == 0:
            messages.error(request, f"Error! No {object_name} objects updated")
        else:
            messages.success(request, f"Success! {len(results)} {object_name} objects updated.")

    return redirect('teamsnap home')

def sync_teamsnapdb_with_teamsnapapi(request):
    '''
    This sync the internal TeamSnap Database with the TeamSnap API
    '''
    TOKEN = request.user.profile.teamsnap_access_token
    USER_ID = request.user.profile.teamsnap_user.id
    TEAM_ID = request.user.profile.teamsnapsettings.managed_team.id
    CLIENT = TeamSnap(token=TOKEN)

    r = {}

    for Obj in [User]:
        r[Obj.__name__] = []
        a = Obj.ApiObject.search(CLIENT, id=USER_ID)
        for _a in a:
            obj, created = Obj.update_or_create_from_teamsnap_api(_a.data)
            r[Obj.__name__].append((obj, created))

    for Obj in [Event, Availability]:
        r[Obj.__name__] = []
        a = Obj.ApiObject.search(CLIENT, team_id=TEAM_ID)
        for _a in a:
            print(f"importing {_a}")
            obj, created = Obj.update_or_create_from_teamsnap_api(_a.data)
            r[Obj.__name__].append((obj, created))


    for object_name, results in r.items():
        if len(r) == 0:
            messages.error(request, f"Error! No {object_name} objects created or updated")
        else:
            result = [created for obj, created in results]
            messages.success(request, f"Success! {sum(result)} {object_name} objects created, {len(result)-sum(result)} {object_name} objects updated.")

    data = {
        'msg': render_to_string('messages.html', {}, request),
    }

    return JsonResponse(data)

def sync_teamsnapdb_to_benchcoachdb(request):
    '''
    This syncs the internal BenchCoach Database and the TeamSnap Database
    '''
    TEAM_ID = request.user.profile.teamsnapsettings.managed_team.id
    r={}

    r['team/opponent'] = []
    for team in Opponent.objects.filter(team_id=TEAM_ID):
        r['team/opponent'] += update_opponent(team, create_benchcoach_object=True, create_related=True)

    for team in Team.objects.filter(id=TEAM_ID):
        r['team/opponent'] += update_team(team, create_benchcoach_object=True, create_related=True)

    r['location'] = []
    for location in Location.objects.filter(team_id=TEAM_ID):
        r['location'] += update_location(location, create_benchcoach_object=True, create_related=True)

    r['member'] = []
    for member in Member.objects.filter(team_id=TEAM_ID, is_non_player=False):
        r['member'] += update_member(member, create_benchcoach_object=True, create_related=True)

    r['event'] = []
    for event in Event.objects.filter(team_id=TEAM_ID):
        r['event'] += update_event(event, create_benchcoach_object=True, create_related=True)

    r['availability'] = []
    for availability in Availability.objects.filter(team_id=TEAM_ID, member__is_non_player=False):
        r['availability'] += update_availability(availability, create_benchcoach_object=True, create_related=True)
    pass

    for object_name, results in r.items():
        if len(r) == 0:
            messages.error(request, f"Error! No {object_name} objects created or updated")
        else:
            result = [created for obj, created in results]
            messages.success(request, f"Success! {sum(result)} {object_name} objects created, {len(result)-sum(result)} {object_name} objects updated.")

    data = {
        'msg': render_to_string('messages.html', {}, request),
    }
    return JsonResponse(data)

from .utils.teamsnap_sync_engine import TeamsnapSyncEngine
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



