from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .models import Event
from .forms import EventForm
from django.http import HttpResponse

def root(request):
    return redirect('/events/schedule')

def list(request):
    events = Event.objects.all()
    context = {
        'title': "Events",
        'items': [
            {
                'id': event.id,
                'title': f'{event.away_team.name} vs. {event.home_team.name}',
                'body':f'{event.start:%a, %b %-d, %-I:%M %p},\n{event.venue.name}',
                'buttons':[
                    {
                        'label':'Edit',
                        'href':reverse('edit event', args=[event.id])
                    },
                    {
                        'label': 'Edit Lineup',
                        'href': reverse('edit lineup', args=[event.id])
                    }
                ]
            }
            for event in events
        ]
    }
    return render(request, 'list.html', context)

def edit(request, id=0):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        if id:
            instance = get_object_or_404(Event, id=id)
            form = EventForm(request.POST or None, instance=instance)
        else:
            form = EventForm(request.POST or None)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            if id == 0: id = None
            new_event, did_create = Event.objects.update_or_create(pk=id, defaults=form.cleaned_data)
            return render(request, 'success.html', {'call_back':reverse('schedule'),'id':new_event.id}, status=201 if did_create else 200)
        else:
            return HttpResponse(status=400)

    # if a GET (or any other method) we'll create a blank form
    else:
        if id:
            instance = get_object_or_404(Event, id=id)
            form = EventForm(request.POST or None, instance=instance)
        else:
            form = EventForm

    return render(request, 'edit.html', {'form': form, 'id': id, 'call_back': 'edit event'})