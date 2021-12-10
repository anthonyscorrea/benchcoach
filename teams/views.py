from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .forms import TeamForm
from .models import Team
from lib.views import BenchcoachListView, BenchcoachEditView

def root(request):
    return redirect(reverse('teams list'))

class TeamsListView(BenchcoachListView):
    Model = Team
    edit_url = 'edit team'
    list_url = 'teams list'
    page_title = "Teams"
    active_tabs = ['opponents_tab']

class TeamEditView(BenchcoachEditView):
    Model = Team
    edit_url = 'edit team'
    list_url = 'teams list'
    Form = TeamForm