from django.contrib import admin

from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.root, name="root"),
    path('list', views.list, name="events list"),
    path('edit/<int:id>', views.edit, name="edit event"),
    path('edit', views.edit, name="edit event"),
    path('edit', views.edit, name="edit event")
]