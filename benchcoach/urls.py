from django.urls import path

from . import views

urlpatterns = [
    path('lineup/edit/<int:event_id>', views.lineup_edit, name="edit lineup"),
    path('events/list', views.EventListView.as_view(), name="event list"),
    path('events/<int:pk>/detail', views.EventDetailView.as_view(), name="event detail"),
    path('players/list', views.PlayerListView.as_view(), name="player list"),
    path('teams/list', views.TeamListView.as_view(), name="team list"),
    path('venues/list', views.VenueListView.as_view(), name="venue list")
]