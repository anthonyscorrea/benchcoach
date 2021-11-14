from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db import models
from django.http import HttpResponse
from django.urls import reverse
from .models import Event
from .forms import EventForm
from django.http import HttpResponse
from lib.views import BenchcoachListView

class EventsListView(BenchcoachListView):
    Model = Event
    edit_url = 'edit player'
    list_url = 'players list'
    page_title = "Players"
    title_strf = '{item.away_team.name} vs. {item.home_team.name}'
    body_strf = "{item.start:%a, %b %-d, %-I:%M %p},\n{item.venue.name}"

    def get_context_data(self):
        context = super().get_context_data()
        for item in context['items']:
            item['buttons'].append(
                {
                    'label': 'Edit Lineup',
                    'href': reverse('edit lineup', args=[item['id']])
                }
            )
        return context

def root(request):
    return redirect('/events/schedule')

def edit(request, id=0):
    Form = EventForm
    Model = Event
    call_back = reverse('events list')
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        if id:
            instance = get_object_or_404(Model, id=id)
            form = Form(request.POST or None, instance=instance)
        else:
            form = Form(request.POST or None)
        if form.is_valid():
            if id == 0: id = None
            new_item, did_create = Model.objects.update_or_create(pk=id, defaults=form.cleaned_data)
            return render(request, 'success.html', {'call_back':call_back,'id':new_item.id}, status=201 if did_create else 200)
        else:
            return HttpResponse(status=400)

    # if a GET (or any other method) we'll create a blank form
    else:
        if id:
            instance = get_object_or_404(Event, id=id)
            form = Form(request.POST or None, instance=instance)
        else:
            form = Form

    return render(request, 'edit.html', {'form': form, 'id': id, 'call_back': 'edit event'})