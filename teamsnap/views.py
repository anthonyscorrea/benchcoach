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
from .utils.teamsnap_object_utils import update_users, update_teams, update_events, update_members, update_locations, update_availabilities
from django.contrib import messages
from django.template.loader import render_to_string
from .utils.import_teamsnap import update_team, update_event, update_member, update_location, update_opponent, update_availability, update_teamsnap_object
from django.forms import modelformset_factory
import django.db.models

def queryset_from_ids(Model, id_list):
    #https://stackoverflow.com/questions/4916851/django-get-a-queryset-from-array-of-ids-in-specific-order
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(id_list)])
    queryset = Model.objects.filter(pk__in=id_list).order_by(preserved)
    return queryset

def edit_event(request, id):
    event = Event.objects.get(id = id)
    return redirect(event.edit_url)

def home(request):
    current_benchcoach_user = request.user
    current_teamsnap_user = request.user.profile.teamsnap_user
    current_teamsnap_team = request.user.profile.teamsnapsettings.managed_team
    context= {
        'benchcoach_user': current_benchcoach_user,
        'teamsnap_user': current_teamsnap_user,
        'teamsnap_team':current_teamsnap_team
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

    for Obj in [Event, Availability, Location, Member, Opponent, Team]:
        r[Obj.__name__] = []
        a = Obj.ApiObject.search(CLIENT, team_id=TEAM_ID)
        for _a in a:
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






