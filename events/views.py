from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Event
from .forms import EventForm
from lib.views import BenchcoachListView, BenchcoachEditView

def root(request):
    return redirect(reverse('events list'))

class EventsListView(BenchcoachListView):
    Model = Event
    edit_url = 'edit event'
    list_url = 'events list'
    page_title = "Events"
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

class EventEditView(BenchcoachEditView):
    Model = Event
    edit_url = 'edit event'
    list_url = 'events list'
    Form = EventForm