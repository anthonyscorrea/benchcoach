from django.contrib import admin
from .models import User, Team, Location, Event, Member, Availability, Opponent

# Register your models here.
admin.site.register(User)
admin.site.register(Team)
admin.site.register(Event)
admin.site.register(Location)
admin.site.register(Member)
admin.site.register(Availability)
admin.site.register(Opponent)