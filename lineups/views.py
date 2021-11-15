from django.shortcuts import render, redirect, get_object_or_404
from .models import Positioning
from .forms import PositioningFormSet
from events.models import Event
from players.models import Player
from django.forms.models import model_to_dict

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
                # form.cleaned_data.pop('id')

                if isinstance(form.cleaned_data['id'], Positioning):
                    positioning_id = form.cleaned_data.pop('id').id #FIXME this is a workaround, not sure why it is necessary
                    positioning = Positioning.objects.filter(id=positioning_id)
                    positioning.update(**form.cleaned_data)
                    did_create = False
                else:
                    positioning = Positioning.objects.create(**form.cleaned_data, event_id=event_id)
                    did_create = True
        return render(request, 'success.html', {'call_back':'edit lineup','id':event_id}, status=200)
            # return render(request, 'success.html', {'call_back':'schedule'})
    event = Event.objects.get(id=event_id)
    players = Player.objects.all().prefetch_related('availability_set', 'statline_set', 'positioning_set')
    players = [
        {
            **model_to_dict(player),
            'availability':player.availability_set.get(event_id=event_id),
            # 'available_value': player.availability_set.get(event_id=event_id).available,
            'statline': player.statline_set.get(player_id=player.id),
            'positioning': player.positioning_set.filter(event_id=event_id).first()
        }
        for player in players
    ]
    players.sort(key=lambda d: (-d['availability'].available, d['last_name']))
    qset = Positioning.objects.filter(event_id=event_id)
    formset = PositioningFormSet(queryset=qset)
    for form in formset:
        for field in form.fields:
            field
    return render(request, 'lineups/lineup.html', {'title': 'Lineup',
                                                   'event': event,
                                                   'players': players,
                                                   'positionings_players_initial':[player for player in players if player['positioning']],
                                                   'positionings_formset':formset})