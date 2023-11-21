from django.contrib import admin
from .models import *
from django.utils import timezone

@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    # list_display = ('id', 'name', 'start', 'end')
    list_display = ('id', 'name', 'start_display', 'end_display')

    def start_display(self, obj):
        return obj.start.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M')

    def end_display(self, obj):
        return obj.end.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M')

    start_display.short_description = 'Start Time'
    end_display.short_description = 'End Time'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')
    list_filter = ('title', 'content')
    search_fields = ('title', 'content')
    ordering = ('title', 'content')

