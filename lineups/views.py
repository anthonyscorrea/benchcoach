from django.shortcuts import render, redirect, get_object_or_404
from .models import Positioning,Availability
from .forms import PositioningFormSet, TeamsnapEventForm
from events.models import Event
from players.models import Player
from django.db.models import Case, When
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Prefetch
from django.db.models import F

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
        is_valid = [f.is_valid() for f in formset]
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
                messages.error(request, f'Error submitting lineup. {form.instance} {form.errors}')
                pass
        if (True in is_valid) and (False in is_valid):
            messages.warning(request, 'Lineup partially submitted.')
        elif (True in is_valid):
            messages.success(request, 'Lineup submitted successfully.')
        elif (True not in is_valid):
            messages.error(request, f'Error submitting lineup.')
        else:
            messages.error(request, f'Error submitting lineup.')
        # return HttpResponse(status=204)
        # return render(request, 'success.html', {'call_back':'edit lineup','id':event_id, 'errors':[error for error in formset.errors if error]}, status=200)
    previous_event = Event.objects.filter(id=event_id-1).first()

    event = Event.objects.get(id=event_id)
    next_event = Event.objects.get(id=event_id+1)
    players = Player.objects.prefetch_related('availability_set', 'positioning_set')

    for player in players:
        Positioning.objects.get_or_create(player_id=player.id, event_id=event_id)

    qs = event.positioning_set.all().filter(player__availability__event=event_id).order_by(
        'order','-player__availability__available','player__last_name').annotate(event_availability=F('player__availability__available'))

    formset = PositioningFormSet(queryset=qs)

    formset_lineup = [f for f in formset if f.instance.order]
    formset_dhd = [f for f in formset if not f.instance.order and f.instance.position]
    formset_bench = [f for f in formset if f not in formset_lineup and f not in formset_dhd]

    teamsnap_form = TeamsnapEventForm(instance=event)

    details = {
        "Away Team": event.away_team,
        "Home Team": event.home_team,
        "Date": event.start.date(),
        "Time": event.start.time(),
        "Venue": event.venue,
        "TeamSnap": teamsnap_form
        # "TeamSnap Link": event.event_set.first()
        # "TeamSnap Link": f'<a href="{reverse("teamsnap edit event", kwargs={"id": event.event_set.first().id})}"> {event.event_set.first()} </a>' if event.event_set.first() else None
    }



    return render(request, 'lineups/lineup.html', {'title': 'Lineup',
                                                   'event': event,
                                                   'details':details,
                                                   'previous_event': previous_event,
                                                   'teamsnap_form': teamsnap_form,
                                                   'next_event': next_event,
                                                   'formset': formset,
                                                   'formset_lineup':formset_lineup,
                                                   'formset_bench':formset_bench,
                                                       'formset_dhd': formset_dhd
                                                   })