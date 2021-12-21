from django.contrib import admin
from .models import Event, Availability, Positioning, Team, Venue, Player, StatLine

# Register your models here.
admin.site.register(Event)
admin.site.register(Availability)
admin.site.register(Positioning)
admin.site.register(Team)
admin.site.register(Venue)
admin.site.register(Player)
admin.site.register(StatLine)