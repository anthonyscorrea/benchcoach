from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Venue

def root(request):
    return redirect('/venues/list')

def list(request):
    venues = Venue.objects.all()
    return render(request, 'list.html', {'title': "Venues", 'items': [(venue.id, f"{venue.name}") for venue in venues], 'edit_url_name': 'edit venue'})

from .forms import VenueForm
def edit(request, id=None):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = VenueForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponse(str(form.cleaned_data))

    # if a GET (or any other method) we'll create a blank form
    else:
        if id:
            instance = get_object_or_404(Venue, id=id)
            form = VenueForm(request.POST or None, instance=instance)
        else:
            form = VenueForm

    return render(request, 'venues/edit.html', {'form': form, 'id':id})