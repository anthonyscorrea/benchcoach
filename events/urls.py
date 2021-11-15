from django.contrib import admin

from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.root, name="root"),
    path('list', views.EventsListView.as_view(), name="events list"),
    path('edit/<int:id>', views.EventEditView.as_view(), name="edit event"),
    path('edit', views.EventEditView.as_view(), name="edit event"),
]