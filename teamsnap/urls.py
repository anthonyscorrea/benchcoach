from django.contrib import admin

from django.urls import path, include
from functools import partial

from . import views

urlpatterns = [
    path('', views.home, name='teamsnap_home'),
    path('edit/event/<int:id>', views.edit_event, name='teamsnap edit event'),
    path('sync/download', views.sync_from_teamsnap, name="sync from teamsnap"),
    path('import/', views.import_teamsnap, name="import"),

    path('<int:team_id>/schedule/', views.schedule, name='teamsnap_schedule'),
    path('<int:team_id>/schedule/view_event/<int:event_id>', views.event, name='teamsnap_view_event'),
    path('<int:team_id>/opponent/view/<int:id>', views.opponent, name='teamsnap_opponent'),
    path('<int:team_id>/location/view/<int:id>', views.location, name='teamsnap_location'),
    path('<int:team_id>/event/<int:event_ids>/edit_lineup/', views.edit_multiple_lineups, name='teamsnap_edit_lineup'),
    path('<int:team_id>/event/<str:event_ids>/edit_lineup/', views.edit_multiple_lineups, name='teamsnap_edit_multiple_lineups'),
    path('<int:team_id>/event/<int:event_id>/submit_lineup/', views.submit_lineup, name='teamsnap_submit_lineup'),
    path('<int:team_id>/event/<int:event_id>/image_generator/', views.image_generator, name='teamsnap_image_generator'),
    path('<int:team_id>/event/<int:event_id>/image_generator/generate', views.get_matchup_image, name='teamsnap_image_generator_generate'),
    path('<int:team_id>/multievent/choose', views.multi_lineup_choose, name='teamsnap_choose_multiple_lineups')
]