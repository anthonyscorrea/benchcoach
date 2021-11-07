from django.shortcuts import render, redirect
from .models import Venue

def root(request):
    return redirect('/venues/list')

def list(request):
    venues = Venue.objects.all()
    return render(request, 'venues/list.html', {'venues': venues})