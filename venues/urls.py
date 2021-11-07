from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.root, name="root"),
    path('list', views.list, name="venues_list")
]