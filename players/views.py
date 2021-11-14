from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .models import Player
from .forms import PlayerForm

# Create your views here.
def root(request):
    return redirect('/players/list')

def list(request):
    items = Player.objects.all()
    context = {
        'title': "Players",
         'items': [
             {'id': item.id,
              'title': f"{item.first_name} {item.last_name}",
              'subtitle': f"{item.jersey_number}",
              'buttons': [
                  {
                      'label': 'Edit',
                      'href': reverse('edit player', args=[item.id])
                  }
              ]
              }
             for item in items]
    }

    return render(request, 'list.html', context)

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
            if id == 0: id = None
            new_player, did_create = Player.objects.update_or_create(pk=id, defaults=form.cleaned_data)
            return render(request, 'success.html', {'call_back':reverse('players list'),'id':new_player.id}, status=201 if did_create else 200)
        else:
            return HttpResponse(status=400)

    # if a GET (or any other method) we'll create a blank form
    else:
        if id:
            instance = get_object_or_404(Player, id=id)
            form = PlayerForm(request.POST or None, instance=instance)
        else:
            form = PlayerForm

    return render(request, 'edit.html', {'form': form, 'id': id, 'call_back':'edit player'})