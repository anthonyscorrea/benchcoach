from django.urls import path, include

from .views import PlayerListView

from . import views

urlpatterns = [
    path('', views.root, name="root"),
    # path('list', views.list, name="players list"),
    path('list', PlayerListView.as_view(), name='players list'),
    path('edit/<int:id>', views.edit, name="edit player"),
    path('edit', views.edit, name="edit player")
]