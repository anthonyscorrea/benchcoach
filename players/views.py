from django.shortcuts import render, redirect
from .models import Player

# Create your views here.
def root(request):
    return redirect('/players/list')

def list(request):
    players = Player.objects.all()
    return render(request, 'list.html', {'title': "Players", 'items': [f"{player.first_name} {player.last_name}" for player in players]})