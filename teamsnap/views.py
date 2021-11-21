from django.shortcuts import render, redirect

# from .teamsnap.api import TeamSnap, Team, Event, Availability
from .models import User, Member, Team, Event, Location
from django.views.generic.list import ListView
from lib.views import BenchcoachListView

def edit_event(request, id):
    event = Event.objects.get(id = id)
    return redirect(event.edit_url)

class EventsListView(BenchcoachListView):
    Model = Event
    edit_url = 'teamsnap edit event'
    list_url = 'teamsnap list events'
    page_title = "TeamSnap Events"
    title_strf = '{item.formatted_title}'
    body_strf = "{item.start_date:%a, %b %-d, %-I:%M %p},\n{item.location.name}"

    # def get_context_data(self):
    #     context = super().get_context_data()
    #     for item in context['items']:
    #         item['buttons'].append(
    #             {
    #                 'label': 'Edit Lineup',
    #                 'href': reverse('edit lineup', args=[item['id']])
    #             }
    #         )
    #     return context

class TeamListView(ListView):
    model = Team

class LocationListView(ListView):
    model = Location