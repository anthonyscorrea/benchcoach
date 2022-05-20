import operator
import time

from django.shortcuts import render, redirect

from .models import User, Member, Team, Event, Location, LineupEntry, Opponent, Availability
from django.http import HttpResponse, HttpResponseNotAllowed
import benchcoach.models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils.teamsnap_sync_engine import TeamsnapSyncEngine
from django.templatetags.static import static
import datetime
import re

@login_required()
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
def dashboard(request, team_id):
    current_benchcoach_user = request.user
    current_teamsnap_user = request.user.profile.teamsnap_user
    current_teamsnap_team = request.user.profile.teamsnapsettings.managed_team
    teamsnap_objects = {}

    TEAM_ID = team_id
    TOKEN = request.user.profile.teamsnap_access_token
    no_past = bool(request.GET.get('no_past', 0))
    games_only = bool(request.GET.get('games_only', 0))
    from pyteamsnap.api import TeamSnap, Event, AvailabilitySummary
    client = TeamSnap(token=TOKEN)
    time.sleep(.5)
    ts_events = Event.search(client, team_id=TEAM_ID)
    ts_availability_summaries_d = {a.data['id']:a for a in AvailabilitySummary.search(client, team_id=team_id)}
    ts_events_future = [e for e in ts_events if e.data['start_date'] > datetime.datetime.now(datetime.timezone.utc)]
    ts_events_past = [e for e in reversed(ts_events) if e.data['start_date'] < datetime.datetime.now(datetime.timezone.utc)]

    return render(request, 'teamsnap/dashboard.html', {
        'team_id':team_id,
        'ts_events_future':ts_events_future,
        'ts_events_past': ts_events_past,
        'events_availabilities' : [(e, ts_availability_summaries_d[e.data['id']]) for e in ts_events_future]
    })

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

@login_required()
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

@login_required()
def schedule(request, team_id):
    TEAM_ID = team_id
    TOKEN = request.user.profile.teamsnap_access_token
    no_past = bool(request.GET.get('no_past', 0))
    games_only = bool(request.GET.get('games_only',0))
    from pyteamsnap.api import TeamSnap, Event, Location, Opponent
    client = TeamSnap(token=TOKEN)
    time.sleep(.5)
    ts_events = Event.search(client, team_id=TEAM_ID)
    if no_past:
        ts_events = [e for e in ts_events if e.data['start_date'] > datetime.datetime.now(datetime.timezone.utc)]
    if games_only:
        ts_events = [e for e in ts_events if e.data['is_game']]
    ts_events = {e.data['id']:e for e in ts_events}
    # ts_opponents = {o.data['id']:o for o in Opponent.search(client, team_id=TEAM_ID)}
    # ts_locations = {l.data['id']:l for l in Location.search(client, team_id=TEAM_ID)}
    # for event in ts_events:

    pass
    return render(request, "teamsnap/schedule.html", context={"events":ts_events.values(), "team_id":team_id})

@login_required()
def event(request, event_id, team_id):
    TOKEN = request.user.profile.teamsnap_access_token

    from pyteamsnap.api import TeamSnap, Event, Availability, Member, EventLineupEntry, EventLineup, AvailabilitySummary
    client = TeamSnap(token=TOKEN)
    time.sleep(0.5)
    ts_bulkload = client.bulk_load(team_id=team_id,
                                   types=[Event, EventLineup, EventLineupEntry, AvailabilitySummary, Member],
                                   event__id=event_id)
    ts_event = [i for i in ts_bulkload if isinstance(i, Event)][0]
    # ts_availabilities = Availability.search(client, event_id=ts_event.data['id'])
    ts_availability_summary = \
        [i for i in ts_bulkload if isinstance(i, AvailabilitySummary) and i.data['event_id'] == event_id][0]
    ts_lineup_entries = [i for i in ts_bulkload if isinstance(i, EventLineupEntry) and i.data['event_id'] == event_id]

    ts_members = [i for i in ts_bulkload if isinstance(i, Member)]
    ts_member_lookup = {m.data['id']: m for m in ts_members}
    # ts_availability_lookup = {m.data['member_id']: m for m in ts_availabilities}
    ts_lineup_entries_lookup = {m.data['member_id']: m for m in ts_lineup_entries}

    members = []

    return render(request, "teamsnap/event/view_event.html", context={
        "availability_summary":ts_availability_summary,
        "event":ts_event,
        "availablities":[],
        "lineup_entries": ts_lineup_entries,
    })

@login_required()
def location(request, id, team_id):
    TOKEN = request.user.profile.teamsnap_access_token

    from pyteamsnap.api import TeamSnap, Location
    client = TeamSnap(token=TOKEN)
    return render(request, "teamsnap/location/view.html", context={"location": Location.get(client, id=id)})
    pass

@login_required()
def opponent(request, team_id, id):
    TOKEN = request.user.profile.teamsnap_access_token

    from pyteamsnap.api import TeamSnap, Opponent
    time.sleep(0.5)
    client = TeamSnap(token=TOKEN)
    return render(request, "teamsnap/opponent.html", context={"opponent": Opponent.get(client, id=id)})
    pass

@login_required()
def edit_lineup(request, event_ids, team_id):
    TOKEN = request.user.profile.teamsnap_access_token
    from django.forms import formset_factory
    from teamsnap.forms import EventChooseForm
    from pyteamsnap.api import TeamSnap, Event, Availability, Member, EventLineupEntry, EventLineup, AvailabilitySummary, Opponent
    client = TeamSnap(token=TOKEN)
    time.sleep(0.5)

    event_ids = str(event_ids).split(",")

    ts_bulkload = client.bulk_load(team_id=team_id,
                                   types=[Event, EventLineup, EventLineupEntry, AvailabilitySummary, Member],
                                   event__id=",".join(event_ids))
    event_ids = [int(i) for i in event_ids]
    formsets_lineup = []
    formsets_bench = []
    formsets = []
    events = []
    contexts = []
    for event_id in event_ids:
        ts_event = [i for i in ts_bulkload if isinstance(i, Event) and i.data['id']==event_id][0]
        ts_availabilities = Availability.search(client, event_id=ts_event.data['id'])
        ts_availability_summary = \
        [i for i in ts_bulkload if isinstance(i, AvailabilitySummary) and i.data['event_id'] == event_id][0]
        ts_lineup_entries = EventLineupEntry.search(client, event_id=event_id)

        if ts_lineup_entries:
            ts_lineup = EventLineup.get(client, id=ts_lineup_entries[0].data['event_lineup_id'])
        else:
            ts_lineup = EventLineup.search(client, event_id=event_id)

        ts_members = [i for i in ts_bulkload if isinstance(i, Member)]
        ts_member_lookup = {m.data['id']: m for m in ts_members}
        ts_availability_lookup = {m.data['member_id']: m for m in ts_availabilities}
        ts_lineup_entries_lookup = {m.data['member_id']: m for m in ts_lineup_entries}

        members=[]

        for member in ts_members:
            members.append ({
                "member":getattr(member, 'data'),
                "availability": getattr(ts_availability_lookup.get(member.data['id'], {}), 'data', {}),
                "lineup_entry": getattr(ts_lineup_entries_lookup.get(member.data['id'], {}), 'data', {})
            }
            )

        members = sorted(members, key=lambda d: (
            {
                None:3, # No Response
                0:2,  # No
                2:1, # Maybe
                1:0 # Yes

            }.get(d['availability'].get('status_code')),
                  d['member'].get('last_name'))
                                   )

        from teamsnap.forms import LineupEntryFormset, LineupEntryForm


        initial = []
        for member in members:
            if not member['member']['is_non_player']:
                initial_member = {}
                if re.search(r'([A-Z0-9]+)(?:\s+\[(.*)\])?', member['lineup_entry'].get('label','')):
                    position, position_note = re.search(r'([A-Z0-9]+)(?:\s+\[(.*)\])?', member['lineup_entry'].get('label','')).groups()
                else:
                    position, position_note = ("","")
                position_only = position_note == "PO"
                initial.append({
                    "event_lineup_entry_id": member['lineup_entry'].get('id'),
                    "event_lineup_id": member['lineup_entry'].get('event_lineup_id'),
                    "event_id": event_id,
                    "position_only": position_only,
                    "member_id": member['member']['id'],
                    "sequence": member['lineup_entry'].get('sequence'),
                    "label": position,
                }

                )

        formset = LineupEntryFormset(
            initial=initial
        )

        for form in formset:
            form.member = ts_member_lookup.get(form['member_id'].initial)
            form.availability = ts_availability_lookup.get(form['member_id'].initial)

        formset_startinglineup = [form for form in formset if form.initial.get('event_lineup_entry_id') and not form.initial.get('position_only')]
        formset_startinglineup = sorted(
            formset_startinglineup,
            key=lambda d: d.initial.get('sequence',100)
        )
        formset_startingpositiononly = [form for form in formset if
                                  form.initial.get('event_lineup_entry_id') and form not in formset_startinglineup]
        formset_startingpositiononly = sorted(
            formset_startingpositiononly,
            key=lambda d: d.initial.get('sequence', 100)
        )
        formset_bench = [form for form in formset if
                         form not in formset_startinglineup and
                         form not in formset_startingpositiononly and
                         form.availability.data['status_code'] in [2, 1]
                         ]
        formset_out = [form for form in formset if
                       form not in formset_startinglineup and
                       form not in formset_bench and
                       form not in formset_startingpositiononly and
                       not form.member.data['is_non_player']
                       ]

        contexts.append({
            "event":ts_event,
            "formset": formset,
            "formset_bench":formset_bench,
            "formset_startinglineup":formset_startinglineup,
            "formset_startingpositionalonly":formset_startingpositiononly,
            "formset_out":formset_out
        })

    return render(request, "teamsnap/lineup/multiple_edit.html", context={
            "team_id": team_id,
            "contexts":contexts
        })

@login_required()
def submit_lineup(request, team_id, event_id):
    from pyteamsnap.api import TeamSnap, EventLineupEntry, EventLineup
    from teamsnap.forms import LineupEntryFormset
    TOKEN = request.user.profile.teamsnap_access_token
    client = TeamSnap(token=TOKEN)
    time.sleep(0.5)
    ts_lineup = EventLineup.search(client, event_id=event_id)
    event_lineup_id = ts_lineup[0].data['id']
    if request.GET:
        return HttpResponseNotAllowed()
    if request.POST:
        formset = LineupEntryFormset(request.POST)
        if formset.is_valid():
            r = []
            for form in formset:
                data = form.cleaned_data
                if data.get('event_lineup_entry_id'):
                    event_lineup_entry = EventLineupEntry.get(client, id=data.get('event_lineup_entry_id'))
                    if data.get('position_only'):
                        data['label'] = data['label'] + ' [PO]'
                    event_lineup_entry.data.update(data)
                    if not data.get('sequence') and not data.get('label'):
                        try:
                            r.append(event_lineup_entry.delete())
                        except Exception as e:
                            raise e
                    else:
                        try:
                            r.append(event_lineup_entry.put())
                        except:
                            pass
                    pass
                elif data.get('sequence') is not None and data.get('label'):
                    event_lineup_entry = EventLineupEntry.new(client)
                    if data.get('position_only'):
                        data['label'] = data['label'] + ' [PO]'
                    event_lineup_entry.data.update(data)
                    event_lineup_entry.data.update({"event_lineup_id": event_lineup_id})
                    try:
                        r.append(event_lineup_entry.post())
                    except Exception as e:
                        raise e
                else:
                    pass
        else:
            # breakpoint()
            pass
        # breakpoint()
        pass
        return HttpResponse(f'{r}')
        pass
    return HttpResponse(f'{team_id} {event_id}')

@login_required()
def image_generator(request, team_id, event_id):
    TOKEN = request.user.profile.teamsnap_access_token

    from pyteamsnap.api import TeamSnap, Event, Availability, Member, EventLineupEntry, EventLineup, AvailabilitySummary
    client = TeamSnap(token=TOKEN)
    time.sleep(0.5)

    ts_event = Event.get(client, id=event_id)
    return render(request, "teamsnap/event/instagen.html", context = {"event":ts_event})

@login_required()
def get_matchup_image(request, team_id, event_id, dimensions=None, background=None):
    from pyteamsnap.api import TeamSnap, EventLineupEntry, EventLineup, Event, Team, Opponent, Location
    from .utils.gen_image import Team as ImagegenTeam, Location as ImagegenLocation
    from .utils.gen_image import gen_image, gen_results_image
    import io
    TOKEN = request.user.profile.teamsnap_access_token
    if request.GET:
        POSTPONED = request.GET.get('postponed', 'false') == 'true'
        INCLUDE_WINLOSS = request.GET.get('winloss', 'false') == 'true'
        BACKGROUND = request.GET.get('background', 'location')
        game_id = event_id
        dimensions = request.GET.get('dimensions')
        width = int(dimensions.split("x")[0])
        height = int(dimensions.split("x")[1])

        teamsnap = TeamSnap(TOKEN)
        time.sleep(0.5)
        ts_event = Event.get(teamsnap, game_id).data
        fave_team = Team.get(teamsnap, ts_event['team_id']).data
        opponent_team = Opponent.get(teamsnap, ts_event['opponent_id']).data
        location = Location.get(teamsnap, ts_event['location_id']).data
        formatted_results = ts_event['formatted_results']
        if formatted_results:
            # L 4-3
            runs_for = formatted_results.split(" ")[1].split("-")[0]
            runs_against = formatted_results.split(" ")[1].split("-")[1]
        else:
            runs_for, runs_against = None, None

        logo_image_directory = 'benchcoachproject/static/teamsnap/ig/logos-bw/{filename}.{ext}'
        venue_image_directory = 'benchcoachproject/static/teamsnap/ig/locations/{filename}.{ext}'

        def shortname_from_name(name):
            return name.replace(" ", "").lower()

        # date = parser.parse(ts_event['start_date'])
        # date = date.astimezone(ZoneInfo("America/Chicago"))
        game_info = {
            "date": ts_event['start_date'],
            "team_fave": ImagegenTeam(
                name=fave_team["name"],
                image_directory=logo_image_directory.format(filename=shortname_from_name(fave_team["name"]), ext="png")
            ),
            "team_opponent": ImagegenTeam(
                name=opponent_team["name"],
                image_directory=logo_image_directory.format(filename=shortname_from_name(opponent_team["name"]),
                                                            ext="png")
            ),
            "location": ImagegenLocation(
                name=location['name'],
                image_directory=venue_image_directory.format(filename=shortname_from_name(location["name"]), ext="png"),
                # address=location['address']
            ),
            "runs_for": runs_for,
            "runs_against": runs_against
        }

        if not game_info['runs_for'] and not game_info['runs_against']:
            image = gen_image(**game_info, background=BACKGROUND, width=width, height=height)
        elif game_info['runs_for'] and game_info['runs_against']:
            image = gen_results_image(**game_info, background=BACKGROUND, width=width, height=height)
        else:
            raise Exception

        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format='PNG')
        imgByteArr = imgByteArr.getvalue()

        return HttpResponse(imgByteArr, content_type="image/png")

@login_required()
def multi_lineup_choose(request, team_id):
    TOKEN = request.user.profile.teamsnap_access_token
    from teamsnap.forms import EventChooseForm
    from django.forms import formset_factory
    from pyteamsnap.api import TeamSnap, Event
    client = TeamSnap(token=TOKEN)

    if request.POST:
        ts_events = Event.search(client, team_id=team_id)
        EventChooseFormset = formset_factory(EventChooseForm)
        formset = EventChooseFormset(request.POST)
        choices = [(e.data['id'], e.data['formatted_title']) for e in ts_events]

        for form in formset:
            form.fields['event_id'].choices = choices

        if formset.is_valid():
            event_ids = [f.cleaned_data['event_id'] for f in formset]
        else:
            event_ids = request.GET.get("event_ids").split(",")
        EventChooseFormset = formset_factory(EventChooseForm)
        formset = EventChooseFormset(request.POST)

        return redirect('teamsnap_edit_multiple_lineups',team_id=team_id, event_ids=",".join(event_ids))
    elif not request.GET.get('num'):
        return HttpResponse(500)
    else:
        num = int(request.GET.get('num'))
    TEAM_ID = team_id
    TOKEN = request.user.profile.teamsnap_access_token
    no_past = bool(request.GET.get('no_past', 0))
    games_only = bool(request.GET.get('games_only', 0))
    from pyteamsnap.api import TeamSnap, Event, Location, Opponent
    client = TeamSnap(token=TOKEN)
    time.sleep(.5)
    ts_events = Event.search(client, team_id=TEAM_ID)
    if no_past:
        ts_events = [e for e in ts_events if e.data['start_date'] > datetime.datetime.now(datetime.timezone.utc)]
    if games_only:
        ts_events = [e for e in ts_events if e.data['is_game']]
    ts_events = {e.data['id']: e for e in ts_events}
    # ts_opponents = {o.data['id']:o for o in Opponent.search(client, team_id=TEAM_ID)}
    # ts_locations = {l.data['id']:l for l in Location.search(client, team_id=TEAM_ID)}
    # for event in ts_events:

    EventChooseFormset = formset_factory(EventChooseForm, extra=num)
    formset = EventChooseFormset()

    choices= [(id, e.data['formatted_title']) for id, e in ts_events.items()]

    for form in formset:
        form.fields['event_id'].choices = choices

    pass
    return render(request, "teamsnap/lineup/multiple_choose.html", context={"formset": formset, "team_id": team_id})