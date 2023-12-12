from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import AvailableBookingDate, UserProfile, Post
from django.utils import timezone


@admin.register(AvailableBookingDate)
class AvailableBookingDateAdmin(admin.ModelAdmin):
    # list_display = ('id', 'name', 'start', 'end')
    list_display = ('id', 'user', 'start_display', 'end_display')

    def start_display(self, obj):
        return obj.start.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M')

    def end_display(self, obj):
        return obj.end.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M')

    start_display.short_description = 'Start Time'
    end_display.short_description = 'End Time'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'sex')

# class UserProfileInline(admin.StackedInline):
#     model = UserProfile
#
#
# class UserAdmin(admin.ModelAdmin):
#     model = User
#     fields = ["username", "first_name", "last_name", "email", "is_staff"]
#     inlines = [UserProfileInline]
#
#
# admin.site.unregister(Group)
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)


# @admin.register(Events)
# class EventsAdmin(admin.ModelAdmin):
#     # list_display = ('id', 'name', 'start', 'end')
#     list_display = ('id', 'name', 'start_display', 'end_display')
#
#     def start_display(self, obj):
#         return obj.start.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M')
#
#     def end_display(self, obj):
#         return obj.end.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M')
#
#     start_display.short_description = 'Start Time'
#     end_display.short_description = 'End Time'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')
    list_filter = ('title', 'content')
    search_fields = ('title', 'content')
    ordering = ('title', 'content')

