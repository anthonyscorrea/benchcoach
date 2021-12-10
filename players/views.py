from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.urls import reverse
from .models import Player
from .forms import PlayerForm
from lib.views import BenchcoachListView, BenchcoachEditView

# Create your views here.

class PlayerListView(BenchcoachListView):
    Model = Player
    edit_url = 'edit player'
    list_url = 'players list'
    page_title = "Players"
    title_strf = "{first_name} {last_name}"
    subtitle_strf = "#{jersey_number}"
    active_tabs = ['members_tab']

def root(request):
    return redirect('/players/list')

class PlayerEditView(BenchcoachEditView):
    Form = PlayerForm
    Model = Player
    edit_url = 'edit player'
    list_url = 'players list'