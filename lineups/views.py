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
                form.cleaned_data.pop('id') #FIXME this is a workaround, not sure why it is necessary
                new_positioning, did_create = Positioning.objects.update_or_create(id=form['id'].data, defaults=form.cleaned_data)
            # return render(request, 'success.html', {'call_back':'schedule'})
    event = Event.objects.get(id=id)
    players = Player.objects.all()
    qset = Positioning.objects.filter(event_id=id, order__isnull = False)
    formset = PositioningFormSet(queryset=qset)
    for form in formset:
        for field in form.fields:
            field
    return render(request, 'lineups/lineup.html', {'title': 'Lineup',
                                                   'event': event,
                                                   'players': players,
                                                   'positionings_formset':formset})