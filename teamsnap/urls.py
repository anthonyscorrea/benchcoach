from django.contrib import admin

from django.urls import path, include
from functools import partial

from . import views

urlpatterns = [
    path('', views.home, name='teamsnap home'),
    path('edit/event/<int:id>', views.edit_event, name='teamsnap edit event'),
    path('sync/download', views.sync_from_teamsnap, name="sync from teamsnap"),
    path('import/', views.import_teamsnap, name="import")
]