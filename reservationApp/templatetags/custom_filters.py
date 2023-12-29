from django import template
from reservationApp.models import Notification

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})


@register.inclusion_tag('notifications/notificationsDropdown.html', takes_context=True)
def showNotificationsInDropdown(context):
    request_user = context['request'].user
    notifications = Notification.objects.filter(toUser=request_user).exclude(hasBeenSeen=True).order_by('-date')
    return {'notifications': notifications}
