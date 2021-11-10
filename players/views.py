from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Player
from .forms import PlayerForm

# Create your views here.
def root(request):
    return redirect('/players/list')

def list(request):
    players = Player.objects.all()
    return render(request, 'list.html', {'title': "Players",
                                         'items': [(player.id, f"{player.first_name} {player.last_name}") for player in players],
                                         'edit_url_name': 'edit player'})

def edit(request, id=0):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        if id:
            instance = get_object_or_404(Player, id=id)
            form = PlayerForm(request.POST or None, instance=instance)
        else:
            form = PlayerForm(request.POST or None)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            new_player, did_create = Player.objects.update_or_create(pk=id, defaults=form.cleaned_data)
            return render(request, 'success.html', {'call_back':'players list'})

    # if a GET (or any other method) we'll create a blank form
    else:
        if id:
            instance = get_object_or_404(Player, id=id)
            form = PlayerForm(request.POST or None, instance=instance)
        else:
            form = PlayerForm

    return render(request, 'edit.html', {'form': form, 'id': id, 'call_back':'edit player'})