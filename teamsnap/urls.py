from django.contrib import admin

from django.urls import path, include

from . import views

urlpatterns = [
    path('events', views.EventsListView.as_view(), name="teamsnap events list")
]