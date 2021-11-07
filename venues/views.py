from django.shortcuts import render, redirect
from .models import Venue

def root(request):
    return redirect('/venues/list')

def list(request):
    venues = Venue.objects.all()
    return render(request, 'list.html', {'title': "Venues", 'items': [f"{venue.name}" for venue in venues]})