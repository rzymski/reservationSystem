from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import AvailableBookingDate, Reservation, UserProfile, Notification, Post
from django.utils import timezone


@admin.register(AvailableBookingDate)
class AvailableBookingDateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'start_display', 'end_display', 'intervalTime', 'breakBetweenIntervals', 'isDeleted')
    list_filter = ('id', 'user', 'start', 'end', 'intervalTime', 'breakBetweenIntervals')
    search_fields = ('id', 'start', 'end', 'intervalTime', 'breakBetweenIntervals')
    ordering = ('id', 'user', 'start', 'end', 'intervalTime', 'breakBetweenIntervals')

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
    list_display = ('id', 'bookingPerson', 'availableBookingDate', 'start_display', 'end_display', 'isAccepted', 'isDeleted')
    list_filter = ('id', 'bookingPerson', 'isAccepted', 'start', 'end', 'availableBookingDate')
    search_fields = ('id', 'bookingPerson__username', 'start', 'end', 'isAccepted')
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
    list_filter = ('user', 'age', 'sex')
    search_fields = ('user__username', 'age', 'sex')
    ordering = ('user', 'age', 'sex')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('fromUser', 'toUser', 'notificationType', 'hasBeenSeen', 'dateDisplay', 'availableBookingDate', 'reservation', 'isDeleted')

    def dateDisplay(self, obj):
        return obj.date.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y')
    dateDisplay.short_description = 'Date of creation'
    dateDisplay.admin_order_field = 'date'











@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')
    list_filter = ('title', 'content')
    search_fields = ('title', 'content')
    ordering = ('title', 'content')

