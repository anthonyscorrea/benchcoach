from django.shortcuts import render, redirect
from .models import Event

def root(request):
    return redirect('/events/schedule')

def schedule(request):
    events = Event.objects.all()
    return render(request, 'events/schedule.html', {'events': events})