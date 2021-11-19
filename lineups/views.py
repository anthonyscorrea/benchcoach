from django.shortcuts import render, redirect, get_object_or_404
from .models import Positioning
from .forms import PositioningFormSet
from events.models import Event
from players.models import Player
from django.forms.models import model_to_dict
from django.db.models import Q

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
    players_info = { player.id:{
        'availability': player.availability_set.get(event_id=event_id),
        'statline': player.statline_set.get(player_id=player.id),
        **model_to_dict(player)
    }
        for player in players
    }
    # players_d.sort(key=lambda d: (-d['availability'].available, d['last_name']))

    players_with_positioning = [i.player for i in Positioning.objects.filter(event_id=event_id)]
    players_without_positioning = [i for i in players if i not in players_with_positioning]
    Positioning.objects.bulk_create([Positioning(event_id=event_id, player=player) for player in players_without_positioning])
    qset = Positioning.objects.filter(event_id=event_id)
    for q in qset:
        q.available= q.player.availability_set.get(player_id=q.player.id, event_id=event_id)
        q.statline = q.player.statline_set.get(player_id=q.player.id)
    formset = PositioningFormSet(queryset=qset.order_by('order'))
    pass
    formset_starting = PositioningFormSet(
        queryset=Positioning.objects.exclude(order__isnull=True).filter(event_id=event_id))
    formset_bench = PositioningFormSet(
        queryset=Positioning.objects.exclude(order__isnull=False).filter(event_id=event_id))

    for f in formset:
        if f.instance.player_id:
            f.availability = f.instance.player.availability_set.get(event_id=event_id)
            # f.statline = f.instance.player.statline_set.get()



    return render(request, 'lineups/lineup.html', {'title': 'Lineup',
                                                   'event': event,
                                                   'players_info': players_info,
                                                   'formset': formset,
                                                   # 'players': players_d,
                                                   # 'positionings_players_initial':[player for player in players if player['positioning']],
                                                   'formset_starting':formset_starting,
                                                   'formset_bench':formset_bench
                                                   })