from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Venue
from .forms import VenueForm

def root(request):
    return redirect('/venues/list')

def list(request):
    venues = Venue.objects.all()
    return render(request, 'list.html', {'title': "Venues", 'items': [(venue.id, f"{venue.name}") for venue in venues], 'edit_url_name': 'edit venue'})


def edit(request, id=0):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        if id:
            instance = get_object_or_404(Venue, id=id)
            form = VenueForm(request.POST or None, instance=instance)
        else:
            form = VenueForm(request.POST or None)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            new_venue, did_create = Venue.objects.update_or_create(pk=id, defaults=form.cleaned_data)
            return render(request, 'success.html', {'call_back':'players list'})

    # if a GET (or any other method) we'll create a blank form
    else:
        if id:
            instance = get_object_or_404(Venue, id=id)
            form = VenueForm(request.POST or None, instance=instance)
        else:
            form = VenueForm

    return render(request, 'edit.html', {'form': form, 'id': id, 'call_back': 'edit venue'})