from django.shortcuts import render

# from .teamsnap.api import TeamSnap, Team, Event, Availability
from .models import User, Member, Team, Event, Location
from django.views.generic.list import ListView


class EventsListView(ListView):
    model = Event

class TeamListView(ListView):
    model = Team

class LocationListView(ListView):
    model = Location