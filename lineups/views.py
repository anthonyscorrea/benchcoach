from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from .models import Positioning
from .forms import PositioningFormSet
from django.http import HttpResponse
from django import forms
from events.models import Event
from players.models import Player

# Create your views here.
def edit(request, id):

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        formset = PositioningFormSet(request.POST)
        for form in formset:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                new_event, did_create = Positioning.objects.update_or_create(player_id=form['player'].data, event_id=id, defaults=form.cleaned_data)
                print (form.cleaned_data)
            # return render(request, 'success.html', {'call_back':'schedule'})
    event = Event.objects.get(id=id)
    players = Player.objects.all()
    qset = Positioning.objects.filter(event_id=id, order__isnull = False)
    formset = PositioningFormSet(queryset=qset)
    return render(request, 'lineups/lineup.html', {'title': 'Lineup',
                                                   'event': event,
                                                   'players': players,
                                                   'positionings_formset':formset})