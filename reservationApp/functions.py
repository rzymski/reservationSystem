from .models import *
from icecream import ic
from django.core.mail import send_mail
import threading


def getReservationWithoutServiceProviderJsonData(reservation):
    return {'title': f"{reservation.bookingPerson.first_name} {reservation.bookingPerson.last_name}",
            'id': reservation.id,
            'start': reservation.start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': reservation.end.strftime('%Y-%m-%dT%H:%M:%S'),
            'backgroundColor': '#FFA500',
            'borderColor': '#FFFFFF',
            'display': 'block',
            'serviceProviderId': -1,
            'serviceProviderNameAndSurname': f"",
            'clientId': reservation.bookingPerson.id,
            'clientNameAndSurname': f"{reservation.bookingPerson.first_name} {reservation.bookingPerson.last_name}",
            'eventType': 3,
            'intervalTimeInt': None,
            'intervalTimeString': None,
            'breakBetweenIntervals': 0,
            'editable': True,
            'availableBookingDateStart': None,
            'availableBookingDateEnd': None}


def getUnconfirmedReservationJsonData(reservation):
    return {'title': f"{reservation.bookingPerson.first_name} {reservation.bookingPerson.last_name}",
            'id': reservation.id,
            'start': reservation.start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': reservation.end.strftime('%Y-%m-%dT%H:%M:%S'),
            'backgroundColor': '#FFA500',
            'borderColor': '#FFFFFF',
            'display': 'block',
            'serviceProviderId': reservation.availableBookingDate.user.id,
            'serviceProviderNameAndSurname': f"{reservation.availableBookingDate.user.first_name} {reservation.availableBookingDate.user.last_name}",
            'clientId': reservation.bookingPerson.id,
            'clientNameAndSurname': f"{reservation.bookingPerson.first_name} {reservation.bookingPerson.last_name}",
            'eventType': 1,
            'intervalTimeInt': reservation.availableBookingDate.intervalTime,
            'intervalTimeString': getTimeStringValue(reservation.availableBookingDate.intervalTime),
            'breakBetweenIntervals': reservation.availableBookingDate.breakBetweenIntervals,
            'editable': False,
            'availableBookingDateStart': reservation.availableBookingDate.start,
            'availableBookingDateEnd': reservation.availableBookingDate.end}


def getConfirmedReservationJsonData(reservation):
    return {'title': f"{reservation.bookingPerson.first_name} {reservation.bookingPerson.last_name}",
            'id': reservation.id,
            'start': reservation.start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': reservation.end.strftime('%Y-%m-%dT%H:%M:%S'),
            'backgroundColor': '#BF40BF',
            'borderColor': '#FFFFFF',
            'display': 'block',
            'serviceProviderId': reservation.availableBookingDate.user.id,
            'serviceProviderNameAndSurname': f"{reservation.availableBookingDate.user.first_name} {reservation.availableBookingDate.user.last_name}",
            'clientId': reservation.bookingPerson.id,
            'clientNameAndSurname': f"{reservation.bookingPerson.first_name} {reservation.bookingPerson.last_name}",
            'eventType': 2,
            'intervalTimeInt': reservation.availableBookingDate.intervalTime,
            'intervalTimeString': getTimeStringValue(reservation.availableBookingDate.intervalTime),
            'breakBetweenIntervals': reservation.availableBookingDate.breakBetweenIntervals,
            'editable': False,
            'availableBookingDateStart': reservation.availableBookingDate.start,
            'availableBookingDateEnd': reservation.availableBookingDate.end}


def getAvailableBookingDateJsonData(availableBookingDate, freeTime, possibleDragging):
    return {'title': f"{availableBookingDate.user.first_name} {availableBookingDate.user.last_name}",
            'id': availableBookingDate.id,
            'start': freeTime[0].strftime('%Y-%m-%dT%H:%M:%S'),
            'end': freeTime[1].strftime('%Y-%m-%dT%H:%M:%S'),
            'backgroundColor': '#3ec336',
            'borderColor': '#FFFFFF',
            'display': 'block',
            'serviceProviderId': availableBookingDate.user.id,
            'serviceProviderNameAndSurname': f"{availableBookingDate.user.first_name} {availableBookingDate.user.last_name}",
            'clientId': -1,
            'clientNameAndSurname': "",
            'eventType': 0,
            'intervalTimeInt': availableBookingDate.intervalTime,
            'intervalTimeString': getTimeStringValue(availableBookingDate.intervalTime),
            'breakBetweenIntervals': availableBookingDate.breakBetweenIntervals,
            'editable': possibleDragging,
            'availableBookingDateStart': None,
            'availableBookingDateEnd': None}


def getAvailableTimeRanges(availableBookingDate):
    reservations = Reservation.objects.filter(availableBookingDate=availableBookingDate, isAccepted=True, isDeleted=False).order_by('start')
    if not reservations:
        return [(availableBookingDate.start, availableBookingDate.end)]
    # Dodanie czasu pomiędzy początkiem pierwszej rezerwacji a początkiem dostępnego czasu
    availableTimeRanges = [(availableBookingDate.start, reservations[0].start)] if availableBookingDate.start != reservations[0].start else []
    # Dodanie czasów pomiędzy koncami poprzednich rezerwacji i poczatkami następnych rezerwacji
    for i in range(len(reservations) - 1):
        startFreeTime = reservations[i].end
        endFreeTime = reservations[i+1].start
        if startFreeTime < endFreeTime:
            availableTimeRanges.append((startFreeTime, endFreeTime))
        if startFreeTime > endFreeTime:
            ic("Wystapil error, ktory nie powinien miec miejsca. Kolejna rezerwacja zaczyna się zanim skończy się poprzednia.")
    # Dodanie czasu pomiędzy koncem ostatniej rezerwacji a końcem dostępnego czasu
    if reservations.last().end != availableBookingDate.end:
        availableTimeRanges.append((reservations.last().end, availableBookingDate.end))
    return availableTimeRanges


def geRangeTimeStrings(start, end, increase):
    values = []
    for i in range(start, end+1, increase):
        # value = f'{i//60} godzin {i%60} minut' if i//60 != 0 else f'{i%60} minut'
        value = ''
        if i // 60:
            value += f'1 godzina' if i//60 == 1 else f'{i//60} godziny'
        if i % 60:
            value += f' {i%60} minut'
        values.append((i, value))
    return values


def getTimeStringValue(timeIntValue):
    if timeIntValue is None:
        return None
    timeStringValue = ''
    if timeIntValue // 60:
        timeStringValue += f'1 godzina' if timeIntValue // 60 == 1 else f'{timeIntValue // 60} godziny'
    if timeIntValue % 60:
        timeStringValue += f' {timeIntValue % 60} minut'
    return timeStringValue


def saveReservationWhichCouldBePartOfAvailableBookingData(reservation, userWhoConfirmedReservation=None):
    availableBookingDate = reservation.availableBookingDate
    try:
        if availableBookingDate.start != reservation.start or availableBookingDate.end != reservation.end:
            availableBookingDateBeforeReservation = None
            availableBookingDateAfterReservation = None
            availableBookingDateInReservationTime = AvailableBookingDate(
                user=availableBookingDate.user,
                start=reservation.start,
                end=reservation.end,
                intervalTime=availableBookingDate.intervalTime,
                breakBetweenIntervals=availableBookingDate.breakBetweenIntervals
            )
            if availableBookingDate.start != reservation.start:
                availableBookingDateBeforeReservation = AvailableBookingDate(
                    user=availableBookingDate.user,
                    start=availableBookingDate.start,
                    end=reservation.start,
                    intervalTime=availableBookingDate.intervalTime,
                    breakBetweenIntervals=availableBookingDate.breakBetweenIntervals
                )
            if availableBookingDate.end != reservation.end:
                availableBookingDateAfterReservation = AvailableBookingDate(
                    user=availableBookingDate.user,
                    start=reservation.end,
                    end=availableBookingDate.end,
                    intervalTime=availableBookingDate.intervalTime,
                    breakBetweenIntervals=availableBookingDate.breakBetweenIntervals
                )
            reservation.availableBookingDate = availableBookingDateInReservationTime
            reservation.isAccepted = True
            otherReservations = Reservation.objects.filter(availableBookingDate=availableBookingDate, isDeleted=False).exclude(id=reservation.id)
            for otherReservation in otherReservations:
                if availableBookingDateBeforeReservation and availableBookingDateBeforeReservation.start <= otherReservation.start and otherReservation.end <= availableBookingDateBeforeReservation.end:
                    otherReservation.availableBookingDate = availableBookingDateBeforeReservation
                elif availableBookingDateAfterReservation and availableBookingDateAfterReservation.start <= otherReservation.start and otherReservation.end <= availableBookingDateAfterReservation.end:
                    otherReservation.availableBookingDate = availableBookingDateAfterReservation
                elif availableBookingDateInReservationTime.start <= otherReservation.start and otherReservation.end <= availableBookingDateInReservationTime.end:
                    otherReservation.availableBookingDate = availableBookingDateInReservationTime
                else:
                    otherReservation.availableBookingDate = None
            availableBookingDate.isDeleted = True
            availableBookingDate.save(fromUser=userWhoConfirmedReservation)
            availableBookingDateInReservationTime.save()
            reservation.save()
            if availableBookingDateBeforeReservation:
                availableBookingDateBeforeReservation.save()
            if availableBookingDateAfterReservation:
                availableBookingDateAfterReservation.save()
            for otherReservation in otherReservations:
                otherReservation.save()
        else:
            reservation.isAccepted = True
            reservation.save()
        createNotificationAndSendMail(0, reservation.bookingPerson, userWhoConfirmedReservation, None, reservation)
        if userWhoConfirmedReservation != reservation.availableBookingDate.user:
            createNotificationAndSendMail(10, reservation.availableBookingDate.user, userWhoConfirmedReservation, reservation.availableBookingDate, reservation)
    except ValidationError as e:
        return e.message


def createNotificationAndSendMail(notificationType, toUser, fromUser, availableBookingDate=None, reservation=None):
    ic("Create notification and send mail")
    notification = Notification.createNotification(notificationType, toUser, fromUser, availableBookingDate, reservation)
    ic(notification)
    subject, message, receivers = getMailData(notification)
    sendMail(subject, message, receivers)


def getMailData(notification):
    activity = ""
    if notification.notificationType == 0:
        activity += 'potwierdził twoją rezerwacje'
    elif notification.notificationType == 1:
        activity += 'zaakceptował twoją propozycje terminu'
    elif notification.notificationType == 2:
        activity += 'zaproponował termin rezerwacji'
    elif notification.notificationType == 3:
        activity += 'anululował potwierdzony termin rezerwacji'
    elif notification.notificationType == 4:
        activity += 'usunął twoją rezerwacje'
    elif notification.notificationType == 5:
        activity += 'usunął twoją propozycje terminu'
    elif notification.notificationType == 6:
        activity += 'usunął twój dostępny termin'
    elif notification.notificationType == 7:
        activity += 'edytował twój dostępny termin'
    elif notification.notificationType == 8:
        activity += 'edytował twoją propozycje terminu'
    elif notification.notificationType == 9:
        activity += 'edytował swój dostępny termin poza przedział twojej rezerwacji'
    elif notification.notificationType == 10:
        activity += 'zaakceptował rezerwacje w twoim terminie'
    fromUser = f"{ notification.fromUser.first_name.capitalize() } { notification.fromUser.last_name.capitalize() } "
    subject = fromUser + activity + "."
    eventData = ""
    if notification.reservation:
        eventData += f"Termin {notification.reservation.start} - {notification.reservation.end}."
    elif notification.availableBookingDate:
        eventData += f"Termin {notification.availableBookingDate.start} - {notification.availableBookingDate.end}."
    messageContent = subject + "\n" + eventData
    receivers = [notification.toUser.email]
    return activity, messageContent, receivers


def sendMail(subject, message, receivers):
    ic(subject, message, receivers)
    EmailThread(subject, message, receivers).start()


class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.message = message
        threading.Thread.__init__(self)

    def run(self):
        send_mail(subject=self.subject, message=self.message, from_email='pracainzynierska@gmail.com', recipient_list=self.recipient_list)
