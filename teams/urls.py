from django.contrib import admin

from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.root, name="root"),
    path('list', views.TeamsListView.as_view(), name="teams list"),
    path('edit/<int:id>', views.TeamEditView.as_view(), name="edit team"),
    path('edit', views.TeamEditView.as_view(), name="edit team")
]