from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('events/list/',  login_required(views.EventListView.as_view()), name="event list"),
    path('events/<int:event_id>/', login_required(views.event), name="event"),
    path('players/list/',  login_required(views.PlayerListView.as_view()), name="player list"),
    path('teams/list/',  login_required(views.TeamListView.as_view()), name="team list"),
    path('venues/list/',  login_required(views.VenueListView.as_view()), name="venue list"),
    path('events/<int:event_id>/card',  login_required(views.lineupcard), name="lineup card"),
    path('events/<int:event_id>/csv',  views.csv_export, name="lineup csv"),
    path('events/<int:event_id>/<str:active_tab>', login_required(views.event), name="event")
]