from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .forms import TeamForm
from .models import Team

def root(request):
    return redirect('/teams/list')

def list(request):
    items = Team.objects.all()
    context = {

        'title': "Teams",
         'items': [
             {'id': item.id,
              'title': f"{item.name}",
              'buttons': [
                  {
                      'label': 'Edit',
                      'href': reverse('edit team', args=[item.id])
                  }
              ]
              }
             for item in items]
    }
    return render(request, 'list.html', context)

def edit(request, id=0):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        if id:
            instance = get_object_or_404(Team, id=id)
            form = TeamForm(request.POST or None, instance=instance)
        else:
            form = TeamForm(request.POST or None)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            new_team, did_create = Team.objects.update_or_create(pk=id, defaults=form.cleaned_data)
            return render(request, 'success.html', {'call_back_url':reverse('teams list'), 'id':new_team.id},status=201 if did_create else 200)

    # if a GET (or any other method) we'll create a blank form
    else:
        if id:
            instance = get_object_or_404(Team, id=id)
            form = TeamForm(request.POST or None, instance=instance)
        else:
            form = TeamForm

    return render(request, 'edit.html', {'form': form, 'id': id, 'call_back':'edit team'})