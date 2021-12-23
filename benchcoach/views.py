from django.shortcuts import render
from .models import Event, Team, Player, Positioning, Venue
from .forms import PositioningFormSet, TeamsnapEventForm
from django.contrib import messages
from django.db.models import F
from django.views.generic import ListView, DetailView

class BenchCoachListView(ListView):
    title = None

class EventDetailView(DetailView):
    model = Event
    context_object_name = "event"
    template_name = 'benchcoach/event-detail.html'

class EventListView(ListView):
    model = Event
    context_object_name = "events"
    template_name = 'benchcoach/event-list.html'

class PlayerListView(ListView):
    model = Player
    template_name = 'benchcoach/player-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Players"
        context['members_tab_active'] ='active'
        return context

class TeamListView(ListView):
    model = Team
    template_name = 'benchcoach/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Teams"
        context['opponents_tab_active'] ='active'
        return context

class VenueListView(ListView):
    model = Venue
    template_name = 'benchcoach/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Venues"
        context['venues_tab_active'] ='active'
        return context

def lineup_edit(request, event_id):

    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        formset = PositioningFormSet(request.POST)
        is_valid = [f.is_valid() for f in formset]
        for form in formset:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:

                if isinstance(form.cleaned_data["id"], Positioning):
                    positioning_id = form.cleaned_data.pop(
                        "id"
                    ).id  # FIXME this is a workaround, not sure why it is necessary
                    positioning = Positioning.objects.filter(id=positioning_id)
                    positioning.update(**form.cleaned_data)
                    did_create = False
                else:
                    positioning = Positioning.objects.create(
                        **form.cleaned_data, event_id=event_id
                    )
                    did_create = True
            else:
                messages.error(
                    request, f"Error submitting lineup. {form.instance} {form.errors}"
                )
                pass
        if (True in is_valid) and (False in is_valid):
            messages.warning(request, "Lineup partially submitted.")
        elif True in is_valid:
            messages.success(request, "Lineup submitted successfully.")
        elif True not in is_valid:
            messages.error(request, f"Error submitting lineup.")
        else:
            messages.error(request, f"Error submitting lineup.")
        # return HttpResponse(status=204)
        # return render(request, 'success.html', {'call_back':'edit lineup','id':event_id, 'errors':[error for error in formset.errors if error]}, status=200)
    previous_event = Event.objects.filter(id=event_id - 1).first()

    event = Event.objects.get(id=event_id)
    next_event = Event.objects.get(id=event_id + 1)
    players = Player.objects.prefetch_related("availability_set", "positioning_set")

    for player in players:
        Positioning.objects.get_or_create(player_id=player.id, event_id=event_id)

    qs = (
        event.positioning_set.all()
        .filter(player__availability__event=event_id, player__teamsnap_member__is_non_player=False)
        .order_by("order", "-player__availability__available", "player__last_name")
        .annotate(event_availability=F("player__availability__available"))
    )

    formset = PositioningFormSet(queryset=qs)

    formset_lineup = [f for f in formset if f.instance.order]
    formset_dhd = [f for f in formset if not f.instance.order and f.instance.position]
    formset_bench = [
        f for f in formset if f not in formset_lineup and f not in formset_dhd
    ]

    details = {
        "Away Team": event.away_team,
        "Home Team": event.home_team,
        "Date": event.start.date(),
        "Time": event.start.time(),
        "Venue": event.venue,
    }

    return render(
        request,
        "benchcoach/lineup.html",
        {
            "title": "Lineup",
            "event": event,
            "details": details,
            "previous_event": previous_event,
            "next_event": next_event,
            "formset": formset,
            "formset_lineup": formset_lineup,
            "formset_bench": formset_bench,
            "formset_dhd": formset_dhd,
        },
    )
