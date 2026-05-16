from django.contrib import admin
from .models import Event, Location, EventPollOption, EventAttendance

admin.site.register(Location)
admin.site.register(Event)
admin.site.register(EventPollOption)
admin.site.register(EventAttendance)
