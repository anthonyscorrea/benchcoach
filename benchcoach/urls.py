from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('lineup/edit/<int:event_id>/', login_required(views.lineup_edit), name="edit lineup"),
    path('lineup/edit/<int:event_id>/<str:active_tab>',  login_required(views.lineup_edit), name="edit lineup"),
    path('events/list/',  login_required(views.EventListView.as_view()), name="event list"),
    path('events/<int:pk>/detail',  login_required(views.EventDetailView.as_view()), name="event detail"),
    path('events/<int:pk>/lineup',  login_required(views.EventDetailView.as_view()), name="event lineup"),
    path('players/list/',  login_required(views.PlayerListView.as_view()), name="player list"),
    path('teams/list/',  login_required(views.TeamListView.as_view()), name="team list"),
    path('venues/list/',  login_required(views.VenueListView.as_view()), name="venue list")
]