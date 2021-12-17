from django.shortcuts import render, redirect

# from .teamsnap.api import TeamSnap, Team, Event, Availability
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

def edit_lineup(request, event_id):

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        formset = LineupEntryFormSet(request.POST)
        for form in formset:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:

                if isinstance(form.cleaned_data['id'], LineupEntry):
                    positioning_id = form.cleaned_data.pop('id').id #FIXME this is a workaround, not sure why it is necessary
                    positioning = LineupEntry.objects.filter(id=positioning_id)
                    positioning.update(**form.cleaned_data)
                    did_create = False
                else:
                    positioning = LineupEntry.objects.create(**form.cleaned_data, event_id=event_id)
                    did_create = True
            else:
                pass
        return render(request, 'success.html', {'call_back':'teamsnap edit lineup','id':event_id, 'errors':[error for error in formset.errors if error]}, status=200)
            # return render(request, 'success.html', {'call_back':'schedule'})
    event = Event.objects.get(id=event_id)
    members = Member.objects.filter(is_non_player=False).prefetch_related('availability_set', 'lineupentry_set')
    # players_d.sort(key=lambda d: (-d['availability'].available, d['last_name']))

    for member in members:
        LineupEntry.objects.get_or_create(member_id=member.id, event_id=event_id)

    qs_starting_lineup = LineupEntry.objects.filter(event_id=event_id, sequence__isnull=False, sequence__gt=0).order_by('sequence')
    qs_bench = LineupEntry.objects.filter(event_id=event_id, sequence=0).prefetch_related('member__availability_set').order_by('member__last_name')

    # This is all a compromise to get the sorting just the way I wanted. THERE'S GOT TO BE A BETTER WAY
    ids_starting_lineup = [item.id for item in qs_starting_lineup]
    ids_bench_available = [item.id for item in qs_bench
                           if item.member.availability_set.get(event_id=event_id).status_code == 1]
    ids_bench_maybe = [item.id for item in qs_bench
                           if item.member.availability_set.get(event_id=event_id).status_code == 2]
    ids_bench_no = [item.id for item in qs_bench
                       if item.member.availability_set.get(event_id=event_id).status_code == 0]
    ids_bench_unknown = [item.id for item in qs_bench
                    if item.member.availability_set.get(event_id=event_id).status_code is None]
    qset = queryset_from_ids(LineupEntry, ids_starting_lineup + ids_bench_available + ids_bench_maybe + ids_bench_no + ids_bench_unknown)

    formset = LineupEntryFormSet(queryset=qset)

    for f in formset:
        if f.instance.member_id:
            f.availability = f.instance.member.availability_set.get(event_id=event_id)
            # f.statline = f.instance.member.statline_set.get()

    formset_lineup = [f for f in formset if f.instance.sequence]
    formset_bench = [f for f in formset if f not in formset_lineup]
    formset_dhd = [f for f in formset if not f.instance.sequence and f.instance.label]

    return render(request, 'teamsnap/lineup.html', {'title': 'Lineup',
                                                   'event': event,
                                                   'formset_lineup': formset_lineup,
                                                    'formset_bench':formset_bench,
                                                    'formset_dhd':formset_dhd
                                                   })