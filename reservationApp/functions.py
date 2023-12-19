from .models import *
from icecream import ic


def getAvailableTimeRanges(availableBookingDate):
    reservations = Reservation.objects.filter(availableBookingDate=availableBookingDate, isAccepted=True).order_by('start')
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
    if timeIntValue == None:
        return None
    timeStringValue = ''
    if timeIntValue // 60:
        timeStringValue += f'1 godzina' if timeIntValue // 60 == 1 else f'{timeIntValue // 60} godziny'
    if timeIntValue % 60:
        timeStringValue += f' {timeIntValue % 60} minut'
    return timeStringValue

