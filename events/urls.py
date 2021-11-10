from django.contrib import admin

from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.root, name="root"),
    path('schedule', views.schedule, name="schedule"),
    path('edit/<int:id>', views.edit, name="edit event"),
    path('edit', views.edit, name="edit event"),
    path('edit', views.edit, name="edit event")
]