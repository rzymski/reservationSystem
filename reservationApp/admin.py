from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import AvailableBookingDate, Reservation, UserProfile, Notification, Post
from django.utils import timezone


@admin.register(AvailableBookingDate)
class AvailableBookingDateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'startDisplay', 'endDisplay', 'intervalTime', 'breakBetweenIntervals', 'isDeleted')
    list_filter = ('user', 'start', 'end', 'intervalTime', 'breakBetweenIntervals', 'id')
    search_fields = ('id', 'user__username', 'start', 'end', 'intervalTime', 'breakBetweenIntervals')
    ordering = ('id', 'user', 'start', 'end', 'intervalTime', 'breakBetweenIntervals')

    def startDisplay(self, obj):
        return obj.start.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y')
    startDisplay.short_description = 'Start Time'
    startDisplay.admin_order_field = 'start'

    def endDisplay(self, obj):
        return obj.end.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y')
    endDisplay.short_description = 'End Time'
    endDisplay.admin_order_field = 'end'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'bookingPerson', 'start_display', 'end_display', 'isAccepted', 'isDeleted', 'availableBookingDateId', 'availableBookingDateUser', 'availableBookingDateStart', 'availableBookingDateEnd')
    list_filter = ('bookingPerson', 'availableBookingDate__user__username', 'isAccepted', 'start', 'end', 'id', 'availableBookingDate__id', 'availableBookingDate__start', 'availableBookingDate__end')
    search_fields = ('id', 'bookingPerson__username', 'start', 'end', 'isAccepted', 'availableBookingDate__id', 'availableBookingDate__user__username', 'availableBookingDate__start', 'availableBookingDate__end')
    ordering = ('id', 'bookingPerson', 'start', 'end', 'isAccepted')

    def start_display(self, obj):
        return obj.start.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y')
    start_display.short_description = 'Start Time'
    start_display.admin_order_field = 'start'

    def end_display(self, obj):
        return obj.end.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y')
    end_display.short_description = 'End Time'
    end_display.admin_order_field = 'end'

    def availableBookingDateId(self, obj):
        return obj.availableBookingDate.id if obj.availableBookingDate else None

    availableBookingDateId.short_description = 'Id availableBookingDate'
    availableBookingDateId.admin_order_field = 'availableBookingDate__id'

    def availableBookingDateUser(self, obj):
        return obj.availableBookingDate.user if obj.availableBookingDate else None

    availableBookingDateUser.short_description = 'ServiceProvider'
    availableBookingDateUser.admin_order_field = 'availableBookingDate__user'

    def availableBookingDateStart(self, obj):
        return obj.availableBookingDate.start.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y') if obj.availableBookingDate else None

    availableBookingDateStart.short_description = 'Available Booking Date Start'
    availableBookingDateStart.admin_order_field = 'availableBookingDate__start'

    def availableBookingDateEnd(self, obj):
        return obj.availableBookingDate.end.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y') if obj.availableBookingDate else None

    availableBookingDateEnd.short_description = 'Available Booking Date End'
    availableBookingDateEnd.admin_order_field = 'availableBookingDate__end'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'sex')
    list_filter = ('user', 'age', 'sex')
    search_fields = ('user__username', 'age', 'sex')
    ordering = ('user', 'age', 'sex')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'fromUser', 'toUser', 'notificationType', 'hasBeenSeen', 'dateDisplay', 'availableBookingDate', 'reservation', 'isDeleted')

    def dateDisplay(self, obj):
        return obj.date.astimezone(timezone.get_current_timezone()).strftime('%H:%M  %a  %d/%m/%Y')
    dateDisplay.short_description = 'Date of creation'
    dateDisplay.admin_order_field = 'date'











# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     list_display = ('title', 'content')
#     list_filter = ('title', 'content')
#     search_fields = ('title', 'content')
#     ordering = ('title', 'content')

