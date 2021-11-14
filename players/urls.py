from django.urls import path, include

from .views import PlayerListView, PlayerEditView

from . import views

urlpatterns = [
    path('', views.root, name="root"),
    path('list', PlayerListView.as_view(), name='players list'),
    path('edit/<int:id>', PlayerEditView.as_view(), name="edit player"),
    path('edit', PlayerEditView.as_view(), name="edit player")
]