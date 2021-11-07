from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import TeamForm
from .models import Team

def root(request):
    return redirect('/teams/list')

def list(request):
    teams = Team.objects.all()
    return render(request, 'list.html', {'title': "Teams", 'items': [(team.id, f"{team.name}") for team in teams], 'edit_url_name':'edit team'})

def edit(request, id=None):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TeamForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponse(str(form.cleaned_data))

    # if a GET (or any other method) we'll create a blank form
    else:
        if id:
            instance = get_object_or_404(Team, id=id)
            form = TeamForm(request.POST or None, instance=instance)
        else:
            form = TeamForm

    return render(request, 'venues/edit.html', {'form': form, 'id':id})