from django.contrib import admin

from django.urls import path, include
from functools import partial

from . import views

urlpatterns = [
    path('', views.home, name='teamsnap home'),
    # path('events', views.EventsListView.as_view(), name="teamsnap list events"),
    # path('event-table', views.EventsTableView.as_view(), name="teamsnap table events"),
    path('table/<str:object>', views.TeamsnapObjTableView.as_view(), name="teamsnap table obj"),
    path('edit/event/<int:id>', views.edit_event, name='teamsnap edit event'),
    path('sync_teamsnap_db', views.sync_teamsnapdb_with_teamsnapapi, name="sync with teamsnapapi"),
    path('sync_benchcoach_db', views.sync_teamsnapdb_to_benchcoachdb, name="sync benchcoach"),
    # path('import_teamsnap', views.import_teamsnap, name="import teamsnap"),
]