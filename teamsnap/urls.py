from django.contrib import admin

from django.urls import path, include
from functools import partial

from . import views

urlpatterns = [
    path('events', views.EventsListView.as_view(), name="teamsnap list events"),
    path('edit/event/<int:id>', views.edit_event, name='teamsnap edit event'),
    path('edit/lineup/<int:event_id>', views.edit_lineup, name='teamsnap edit lineup')
]