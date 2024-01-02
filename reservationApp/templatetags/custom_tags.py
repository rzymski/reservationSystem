from django import template
from reservationApp.models import Notification

register = template.Library()


@register.inclusion_tag('notifications/notificationsDropdown.html', takes_context=True)
def showNotificationsInDropdown(context):
    request_user = context['request'].user
    notifications = Notification.objects.filter(toUser=request_user, isDeleted=False).order_by('-date')
    notificationsWithContent = []
    for notification in notifications:
        content = None
        if notification.notificationType == 0:
            content = 'potwierdził twoją rezerwacje'
        elif notification.notificationType == 1:
            content = 'zaakceptował twoją propozycje terminu'
        elif notification.notificationType == 2:
            content = 'zaproponował termin rezerwacji'
        elif notification.notificationType == 3:
            content = 'anululował potwierdzony termin rezerwacji'
        elif notification.notificationType == 4:
            content = 'usunął twoją rezerwacje'
        elif notification.notificationType == 5:
            content = 'usunął twoją propozycje terminu'
        elif notification.notificationType == 6:
            content = 'usunął twój dostępny termin'
        elif notification.notificationType == 7:
            content = 'edytował twój dostępny termin'
        elif notification.notificationType == 8:
            content = 'edytował twoją propozycje terminu'
        elif notification.notificationType == 9:
            content = 'edytował swój dostępny termin poza przedział twojej rezerwacji'
        elif notification.notificationType == 10:
            content = 'zaakceptował rezerwacje w twoim terminie'
        else:
            print("NIE POWINNO BYC TAKIEJ OPCJI")
        notification.content = content
        if notification.reservation:
            notification.event = notification.reservation
        else:
            notification.event = notification.availableBookingDate
        notificationsWithContent.append(notification)
    numberOfNotificationsHasNotBeenSeen = Notification.objects.filter(toUser=request_user, isDeleted=False, hasBeenSeen=False).count()
    return {'notifications': notificationsWithContent, 'numberOfNotificationsHasNotBeenSeen': numberOfNotificationsHasNotBeenSeen}
