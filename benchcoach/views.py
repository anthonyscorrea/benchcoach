from django.shortcuts import render, HttpResponse
from .models import Event, Team, Player, Positioning, Venue
from .forms import PositioningFormSet, TeamsnapEventForm
from django.contrib import messages
from django.db.models import F
from django.views.generic import ListView, DetailView
import csv


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

def event(request, event_id, active_tab='details'):
    '''
    Event is the main page for showing an event.
    :param request: django request
    :param event_id: The Bench Coach event ID to display
    :param active_tab: The desired active tab, supports "lineup" and "details"
    :return: 'details' renders a page with event information, 'lineup' with lineup information.
    Either gives context to the template with the event information and formset for the lineup.
    '''

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
        "benchcoach/event.html",
        {
            "title": "Lineup",
            "active_tab":active_tab,
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

def lineupcard(request, event_id):
    '''
    Lineup Card is an first attempt at replicating the "Lineup Card" from Google sheets.
    It is incomplete.
    :param request:
    :param event_id: The Event ID to generate
    :return: It generates a page layout. The context has info for event, event details, starting players and all players (both as a queryset)
    '''
    previous_event = Event.objects.filter(id=event_id - 1).first()

    event = Event.objects.get(id=event_id)
    next_event = Event.objects.get(id=event_id + 1)
    players = Player.objects.prefetch_related("availability_set", "positioning_set")

    for player in players:
        Positioning.objects.get_or_create(player_id=player.id, event_id=event_id)

    qs = (
        event.positioning_set.all()
        .filter(player__availability__event=event_id, player__teamsnap_member__is_non_player=False)
        .order_by("-player__availability__available", "player__last_name", "order")
        .annotate(event_availability=F("player__availability__available"))
    )

    qs_starting = qs.filter(order__isnull=False).order_by("order")

    details = {
        "Away Team": event.away_team,
        "Home Team": event.home_team,
        "Date": event.start.date(),
        "Time": event.start.time(),
        "Venue": event.venue,
    }

    return render(
        request,
        "benchcoach/card.html",
        {
            "title": "Lineup",
            "event": event,
            "details": details,
            "previous_event": previous_event,
            "next_event": next_event,
            "positionings": qs,
            "positionings_starting": qs_starting,
            "empty_lines": range(14)
        },
    )

def csv_export(request, event_id):
    '''
    Exports a CSV to interface with the Google Sheet. The idea is to bring lineup info into the sheet for backwards compatibility.
    The row numbers follow each line as comments.
    :param request:
    :param event_id:
    :return: A CSV file.
    '''
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename=lineup-event-{event_id}.csv'},
    )
    previous_event = Event.objects.filter(id=event_id - 1).first()

    event = Event.objects.get(id=event_id)
    players = Player.objects.prefetch_related("availability_set", "positioning_set")

    for player in players:
        Positioning.objects.get_or_create(player_id=player.id, event_id=event_id)

    qs = (
        event.positioning_set.all()
            .filter(player__availability__event=event_id, player__teamsnap_member__is_non_player=False)
            .order_by("-player__availability__available", "player__last_name", "order")
            .annotate(event_availability=F("player__availability__available"))
    )

    rows = []
                                                                                    # Row number (starts at row 2)
    rows.append(event.teamsnap_event.csv_event_title)                               # 2
    rows.append(event.venue.name)                                                   # 3
    [rows.append('') for i in range(3)]                                             # 4-6
    p = qs.filter(position='P').first()
    if p:
        rows.append(f"{p.player.last_name}, {p.player.first_name}")                 # 7
    else:
        rows.append('')
    [rows.append('') for i in range(3)]                                             # 8-10
    for pos in ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF', 'DH']:               # 11-19
        p = qs.filter(position=pos).first()
        if p:
            rows.append(f"{p.player.last_name}, {p.player.first_name}")
        else:
            rows.append('')
    ehs = qs.filter(position='EH')
    if len(ehs) > 0:
        p=qs.filter(position='EH')[0]
        rows.append(f"{p.player.last_name}, {p.player.first_name}")                 # 20
    else:
        rows.append('')
    if len(ehs) > 1:
        p=qs.filter(position='EH')[1]
        rows.append(f"{p.player.last_name}, {p.player.first_name}")                 # 21
    else:
        rows.append('')
    rows.append('') #22
    p=qs.filter(position__isnull=False, order=0).first()
    if p:
        rows.append(f"{p.player.last_name}, {p.player.first_name}")                 # 23
    else:
        rows.append('')
    rows.append('')                                                                 # 24
    for p in qs.filter(order__gt=0).order_by('order'):                              # 25-34
        rows.append(f"{p.player.last_name}, {p.player.first_name}")

    writer = csv.writer(response)
    for row in rows:
        writer.writerow([row])
    return response