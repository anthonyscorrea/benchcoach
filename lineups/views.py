from django.shortcuts import render, redirect, get_object_or_404
from .models import Positioning
from .forms import PositioningFormSet
from events.models import Event
from players.models import Player
from django.db.models import Case, When
from django.urls import reverse

def queryset_from_ids(Model, id_list):
    #https://stackoverflow.com/questions/4916851/django-get-a-queryset-from-array-of-ids-in-specific-order
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(id_list)])
    queryset = Model.objects.filter(pk__in=id_list).order_by(preserved)
    return queryset

# Create your views here.
def edit(request, event_id):

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        formset = PositioningFormSet(request.POST)
        for form in formset:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:

                if isinstance(form.cleaned_data['id'], Positioning):
                    positioning_id = form.cleaned_data.pop('id').id #FIXME this is a workaround, not sure why it is necessary
                    positioning = Positioning.objects.filter(id=positioning_id)
                    positioning.update(**form.cleaned_data)
                    did_create = False
                else:
                    positioning = Positioning.objects.create(**form.cleaned_data, event_id=event_id)
                    did_create = True
            else:
                pass
        return render(request, 'success.html', {'call_back':'edit lineup','id':event_id, 'errors':[error for error in formset.errors if error]}, status=200)
    previous_event = Event.objects.filter(id=event_id-1).first()

    event = Event.objects.get(id=event_id)
    next_event = Event.objects.get(id=event_id+1)
    players = Player.objects.prefetch_related('availability_set', 'positioning_set')
    positionings = Positioning.objects.filter(event_id=event_id)

    for player in players:
        Positioning.objects.get_or_create(player_id=player.id, event_id=event_id)

    qs_starting_lineup = positionings.filter(order__isnull=False).order_by(
        'order').prefetch_related(
        'player__availability_set')
    qs_bench = positionings.filter(order__isnull=True).prefetch_related(
        'player__availability_set').order_by('player__last_name')

    # This is all a compromise to get the sorting just the way I wanted. THERE'S GOT TO BE A BETTER WAY
    ids_starting_lineup = [item.id for item in qs_starting_lineup]
    ids_bench_available = [item.id for item in qs_bench
                           if item.player.availability_set.get(event_id=event_id).available == 2]
    ids_bench_maybe = [item.id for item in qs_bench
                       if item.player.availability_set.get(event_id=event_id).available == 1]
    ids_bench_no = [item.id for item in qs_bench
                    if item.player.availability_set.get(event_id=event_id).available == 0]
    ids_bench_unknown = [item.id for item in qs_bench
                         if item.player.availability_set.get(event_id=event_id).available == -1]
    qset = queryset_from_ids(Positioning,
                             ids_starting_lineup + ids_bench_available + ids_bench_maybe + ids_bench_no + ids_bench_unknown)

    formset = PositioningFormSet(queryset=qset)

    for f in formset:
        if f.instance.player_id:
            f.availability = f.instance.player.availability_set.get(event_id=event_id)
            # f.statline = f.instance.player.statline_set.get()

    formset_lineup = [f for f in formset if f.instance.order]
    formset_dhd = [f for f in formset if not f.instance.order and f.instance.position]
    formset_bench = [f for f in formset if f not in formset_lineup and f not in formset_dhd]

    details = {
        "Away Team": event.away_team,
        "Home Team": event.home_team,
        "Date": event.start.date(),
        "Time": event.start.time(),
        "Venue": event.venue,
        # "TeamSnap Link": event.event_set.first()
        "TeamSnap Link": f'<a href="{reverse("teamsnap edit event", kwargs={"id": event.event_set.first().id})}"> {event.event_set.first()} </a>' if event.event_set.first() else None
    }

    return render(request, 'lineups/lineup.html', {'title': 'Lineup',
                                                   'event': event,
                                                   'details':details,
                                                   'previous_event': previous_event,
                                                   'next_event': next_event,
                                                   'formset': formset,
                                                   'formset_lineup':formset_lineup,
                                                   'formset_bench':formset_bench,
                                                       'formset_dhd': formset_dhd
                                                   })