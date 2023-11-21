from django.contrib import admin
from .models import *

@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start', 'end')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')
    list_filter = ('title', 'content')
    search_fields = ('title', 'content')
    ordering = ('title', 'content')

