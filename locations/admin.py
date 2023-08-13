from django.contrib import admin

from locations.models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = [
        'address',
     ]
    list_display = [
         'address',
         'lat',
         'lon',
         'request_date',
     ]
    ordering = ['request_date']