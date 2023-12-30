from .models import *
from icecream import ic


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
        Notification.createNotification(0, reservation.bookingPerson, userWhoConfirmedReservation, None, reservation)
        if userWhoConfirmedReservation != reservation.availableBookingDate.user:
            Notification.createNotification(10, reservation.availableBookingDate.user, userWhoConfirmedReservation, reservation.availableBookingDate, reservation)
    except ValidationError as e:
        return e.message
