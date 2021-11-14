from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.root, name="root"),
    path('list', views.VenueListView.as_view(), name="venues list"),
    path('edit/<int:id>', views.VenueEditView.as_view(), name="edit venue"),
    path('edit', views.VenueEditView.as_view(), name="edit venue")
]