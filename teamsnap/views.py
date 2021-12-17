from django.shortcuts import render, redirect

from .teamsnap.api import Event as TsApiEvent
from .teamsnap.api import TeamSnap
from .models import User, Member, Team, Event, Location, LineupEntry
from django.views.generic.list import ListView
from lib.views import BenchcoachListView
from .forms import LineupEntryForm, LineupEntryFormSet, EventForm, EventFormSet
from django.forms.models import model_to_dict
from django.urls import reverse
from django.db.models import Case, When
from django.views import View
from django.http import HttpResponse
from benchcoach.models import Profile as BenchcoachUser
from events.models import Event as BenchcoachEvent
import teamsnap.teamsnap.api
import json
from django.http import JsonResponse
from .utils.import_teamsnap import update_users, update_teams, update_events, update_members, update_locations, update_availabilities

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
    TOKEN = BenchcoachUser.objects.get(id=1).teamsnap_access_token
    CLIENT = TeamSnap(token=TOKEN)
    teamsnap_event_id=request.POST.get('teamsnap event')
    benchcoach_event_id=request.POST.get('teamsnap event')
    if teamsnap_event_id:
        benchcoach_event = BenchcoachEvent.objects.get(id=benchcoach_event_id)
        teamsnap_object = Event.objects.get(id=teamsnap_event_id)
        teamsnap_id = teamsnap_object.teamsnap_id
        teamsnap_response = TsApiEvent.search(client=CLIENT, id=teamsnap_id)
        if teamsnap_response[0]:
            data = teamsnap_response[0].data
            location = Location.objects.get(teamsnap_id=data['location_id'])
            opponent = Team.objects.get(teamsnap_id=data['opponent_id'])

    return HttpResponse(f'Success, {data}')

def sync_teamsnap(request):
    TOKEN = request.user.profile.teamsnap_access_token
    USER_ID = request.user.profile.teamsnap_user.id
    TEAM_ID = request.user.profile.teamsnapsettings.managed_team.id
    CLIENT = TeamSnap(token=TOKEN)
    l = []
    l += update_users(CLIENT, id=USER_ID)
    l += update_teams(CLIENT, team_id=TEAM_ID)
    l += update_members(CLIENT, team_id=TEAM_ID)
    l += update_locations(CLIENT, team_id=TEAM_ID)
    l += update_events(CLIENT, team_id=TEAM_ID)
    l += update_availabilities(CLIENT, team_id=TEAM_ID)

    return JsonResponse({'number of objects updated':len(l)})






