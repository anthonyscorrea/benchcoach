from django.contrib import admin

from django.urls import path, include
from functools import partial

from . import views

urlpatterns = [
    path('', views.home, name='teamsnap home'),
    path('events', views.EventsListView.as_view(), name="teamsnap list events"),
    path('events-table', views.EventsTableView.as_view(), name="teamsnap table events"),
    path('edit/event/<int:id>', views.edit_event, name='teamsnap edit event'),
    path('sync_teamsnap_db', views.sync_teamsnap_db, name="sync teamsnap db"),
    # path('import_teamsnap', views.import_teamsnap, name="import teamsnap"),
]