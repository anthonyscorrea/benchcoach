from django.contrib import admin

from django.urls import path, include

from . import views

urlpatterns = [
    path('edit/<int:event_id>', views.edit, name="edit lineup"),
]