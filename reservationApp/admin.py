from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import AvailableBookingDate, Reservation, UserProfile, Post
from django.utils import timezone


@admin.register(AvailableBookingDate)
class AvailableBookingDateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'start_display', 'end_display')
    list_filter = ('id', 'user', 'start', 'end')
    search_fields = ('id', 'start', 'end')
    ordering = ('id', 'user', 'start', 'end')

    def start_display(self, obj):
        return obj.start.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y')
    start_display.short_description = 'Start Time'
    start_display.admin_order_field = 'start'

    def end_display(self, obj):
        return obj.end.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y')
    end_display.short_description = 'End Time'
    end_display.admin_order_field = 'end'

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'bookingPerson', 'availableBookingDate', 'start_display', 'end_display', 'isAccepted')
    list_filter = ('id', 'bookingPerson', 'availableBookingDate', 'start', 'end', 'isAccepted')
    search_fields = ('id', 'start', 'end', 'isAccepted')
    ordering = ('id', 'bookingPerson', 'availableBookingDate', 'start', 'end', 'isAccepted')

    def start_display(self, obj):
        return obj.start.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y')
    start_display.short_description = 'Start Time'
    start_display.admin_order_field = 'start'

    def end_display(self, obj):
        return obj.end.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y')
    end_display.short_description = 'End Time'
    end_display.admin_order_field = 'end'


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

