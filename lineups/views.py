from django.shortcuts import render
from django.http import HttpResponse
from events.models import Event
from players.models import Player

# Create your views here.
def edit(request, id):
    event = Event.objects.get(id=id)
    players = Player.objects.all()
    print(event)
    return render(request, 'lineups/lineup.html', {'title': 'Lineup', 'event': event, 'players': players, 'lineup':[]})