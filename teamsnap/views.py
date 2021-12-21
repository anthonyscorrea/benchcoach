from django.shortcuts import render, redirect

from .teamsnap.api import Event as TsApiEvent
from .teamsnap.api import TeamSnap
from .models import User, Member, Team, Event, Location, LineupEntry, Opponent, Availability
from lib.views import BenchcoachListView
from .forms import LineupEntryForm, LineupEntryFormSet, EventForm, EventFormSet
from django.urls import reverse
from django.db.models import Case, When
from django.views import View
from django.http import HttpResponse
import benchcoachproject.models
import benchcoach.models
import teamsnap.teamsnap.api
import json
from django.http import JsonResponse
from .utils.teamsnap_object_utils import update_users, update_teams, update_events, update_members, update_locations, update_availabilities
from django.contrib import messages
from django.template.loader import render_to_string
from .utils.import_teamsnap import update_team, update_event, update_member, update_location, update_opponent, update_availability, update_teamsnap_object

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

class EventsTableView(View):
    def get(self, request):
        qs = Event.objects.all()
        formset = EventFormSet(queryset=qs)
        return render(request,'teamsnap/event-table.html', context={'formset':formset})

class EventsListView(BenchcoachListView):
    Model = Event
    edit_url = 'teamsnap edit event'
    list_url = 'teamsnap list events'
    page_title = "TeamSnap Events"
    title_strf = '{item.formatted_title}'
    body_strf = "{item.start_date:%a, %b %-d, %-I:%M %p},\n{item.location.name}"

    def get_context_data(self):
        context = super().get_context_data()
        for item in context['items']:
            item['buttons'].append(
                {
                    'label': 'Edit Lineup',
                    'href': reverse('teamsnap edit lineup', args=[item['id']])
                }
            )
        return context

class TeamListView(BenchcoachListView):
    Model = Team
    edit_url = 'teamsnap edit team'
    list_url = 'teamsnap list teams'
    page_title = "TeamSnap Teams"

class LocationListView(BenchcoachListView):
    Model = Location
    edit_url = 'teamsnap edit location'
    list_url = 'teamsnap list locations'
    page_title = "TeamSnap Locations"

def update_from_teamsnap_event(request):
    TOKEN = benchcoachproject.models.User.objects.get(id=1).teamsnap_access_token
    CLIENT = TeamSnap(token=TOKEN)
    teamsnap_event_id=request.POST.get('teamsnap event')
    benchcoach_event_id=request.POST.get('teamsnap event')
    if teamsnap_event_id:
        benchcoach_event = benchcoach.models.Event.objects.get(id=benchcoach_event_id)
        teamsnap_object = benchcoach.models.Event.objects.get(id=teamsnap_event_id)
        teamsnap_id = teamsnap_object.teamsnap_id
        teamsnap_response = TsApiEvent.search(client=CLIENT, id=teamsnap_id)
        if teamsnap_response[0]:
            data = teamsnap_response[0].data
            location = Location.objects.get(teamsnap_id=data['location_id'])
            opponent = Team.objects.get(teamsnap_id=data['opponent_id'])

    return HttpResponse(f'Success, {data}')

def sync_with_teamsnap_api(request):
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

def sync_teamsnap_db(request):
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
        r['team/location'] += update_location(location, create_benchcoach_object=True, create_related=True)

    r['member'] = []
    for member in Member.objects.filter(team_id=TEAM_ID, is_non_player=False):
        r['member'] += update_member(member, create_benchcoach_object=True, create_related=True)

    r['event'] = []
    for event in Event.objects.filter(team_id=TEAM_ID):
        r['event'] += update_event(event, create_benchcoach_object=True, create_related=True)

    r['availability'] = []
    for availability in Availability.objects.filter(team_id=TEAM_ID):
        r['availability'] += update_availability(availability, create_benchcoach_object=True, create_related=True)

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






