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
        else:
            ic("Wystapil error, ktory nie powinien miec miejsca. Kolejna rezerwacja zaczyna się zanim skończy się poprzednia.")
    # Dodanie czasu pomiędzy koncem ostatniej rezerwacji a końcem dostępnego czasu
    if reservations.last().end != availableBookingDate.end:
        availableTimeRanges.append((reservations.last().end, availableBookingDate.end))
    return availableTimeRanges
