from django.contrib import admin
from .models import User, Team, Location, Event, Member

# Register your models here.
admin.site.register(User)
admin.site.register(Team)
admin.site.register(Event)
admin.site.register(Location)
admin.site.register(Member)