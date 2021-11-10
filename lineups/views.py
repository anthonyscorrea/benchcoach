from django.shortcuts import render
from django.forms import formset_factory
from .forms import PositioningForm
from django.http import HttpResponse
from events.models import Event
from players.models import Player

# Create your views here.
def edit(request, id):
    event = Event.objects.get(id=id)
    players = Player.objects.all()
    PositioningFormSet = formset_factory(PositioningForm, extra=9)
    formset = PositioningFormSet()
    print(event)
    return render(request, 'lineups/lineup.html', {'title': 'Lineup',
                                                   'event': event,
                                                   'players': players,
                                                   'positionings_formset':formset})