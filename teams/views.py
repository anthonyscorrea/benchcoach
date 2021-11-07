from django.shortcuts import render, redirect
from .models import Team

def root(request):
    return redirect('/teams/list')

def list(request):
    teams = Team.objects.all()
    return render(request, 'list.html', {'title': "Teams", 'items': [f"{team.name}" for team in teams]})