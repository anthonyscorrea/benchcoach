from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from .models import Venue
from .forms import VenueForm
from lib.views import BenchcoachListView, BenchcoachEditView

def root(request):
    return redirect('/venues/list')

class VenueListView(BenchcoachListView):
    Model = Venue
    edit_url = 'edit venue'
    list_url = 'venues list'
    page_title = "Venues"

class VenueEditView(BenchcoachEditView):
    Model = Venue
    edit_url = 'edit venue'
    list_url = 'venues list'
    Form = VenueForm