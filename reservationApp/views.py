from django.shortcuts import render, redirect
from .models import *
from .functions import *
from .forms import CreateUserForm, UpdateProfileForm, UpdateUserForm, LoginForm
from .decorators import unauthenticatedUser, allowedUsers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, timedelta
from icecream import ic
import json


def index(request):
    serviceProviders = User.objects.filter(availablebookingdate__isnull=False).distinct()
    serviceProvidersWithImages = []
    for serviceProvider in serviceProviders:
        userProfileObject = UserProfile.objects.get(user=serviceProvider)
        profileImageUrl = userProfileObject.profileImage.url if userProfile and userProfileObject.profileImage else None
        serviceProvidersWithImages.append((serviceProvider, profileImageUrl))

    context = {
        'serviceProvidersWithImages': serviceProvidersWithImages,
        'rangeFrom15to180increasesBy15': geRangeTimeStrings(15, 180, 15),
    }
    return render(request, 'calendar/calendar.html', context)


def allReservationsWithoutServiceProvider(request):
    reservations = Reservation.objects.filter(availableBookingDate__isnull=True)
    out = []
    for reservation in reservations:
        out.append({
            'title': f"{reservation.bookingPerson.first_name} {reservation.bookingPerson.last_name}",
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
            'availableBookingDateEnd': None,
        })
    return JsonResponse(out, safe=False)


def allUnconfirmedReservations(request, allServiceProviders=True, selectedIds=None):
    reservations = Reservation.objects.filter(isAccepted=False, availableBookingDate__isnull=False) if allServiceProviders else Reservation.objects.filter(isAccepted=False, availableBookingDate__isnull=False, availableBookingDate__user__id__in=selectedIds)
    out = []
    for reservation in reservations:
        out.append({
            'title': f"{reservation.bookingPerson.first_name} {reservation.bookingPerson.last_name}",
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
            'availableBookingDateEnd': reservation.availableBookingDate.end,
        })
    return JsonResponse(out, safe=False)


def allConfirmedReservations(request, allServiceProviders=True, selectedIds=None):
    reservations = Reservation.objects.filter(isAccepted=True) if allServiceProviders else Reservation.objects.filter(isAccepted=True, availableBookingDate__user__id__in=selectedIds)
    out = []
    for reservation in reservations:
        out.append({
            'title': f"{reservation.bookingPerson.first_name} {reservation.bookingPerson.last_name}",
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
            'availableBookingDateEnd': reservation.availableBookingDate.end,
        })
    return JsonResponse(out, safe=False)


def allAvailableBookingDates(request, allServiceProviders=True, selectedIds=None):
    availableBookingDates = AvailableBookingDate.objects.all() if allServiceProviders else AvailableBookingDate.objects.filter(user__id__in=selectedIds)
    out = []
    for availableBookingDate in availableBookingDates:
        freeTimesInAvailableBookingDate = getAvailableTimeRanges(availableBookingDate)
        for freeTime in freeTimesInAvailableBookingDate:
            possibleDragging = True if Reservation.objects.filter(isAccepted=True, availableBookingDate=availableBookingDate).count() == 0 else False
            out.append({
                'title': f"{availableBookingDate.user.first_name} {availableBookingDate.user.last_name}",
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
                'availableBookingDateEnd': None,
            })
    return JsonResponse(out, safe=False)


def filterServiceProviders(request):
    if request.method == 'POST':
        selectedOptionsJson = request.POST.get('selectedOptions')
        selectedOptions = json.loads(selectedOptionsJson)
        ic(selectedOptions)
        selectedIds = [option for option in selectedOptions]
        if len(selectedIds) == 0:
            selectedIds = [user.id for user in User.objects.filter(availablebookingdate__isnull=False).distinct()]
            ic(selectedIds)
            # return JsonResponse({'error': 'No selected options'})
        allAvailableBookingDatesJSON = allAvailableBookingDates(request, allServiceProviders=False, selectedIds=selectedIds)
        allUnconfirmedReservationsJSON = allUnconfirmedReservations(request, allServiceProviders=False, selectedIds=selectedIds)
        allConfirmedReservationsJSON = allConfirmedReservations(request, allServiceProviders=False, selectedIds=selectedIds)
        allReservationsWithoutServiceProviderJSON = allReservationsWithoutServiceProvider(request, allServiceProviders=False, selectedIds=selectedIds)
        combinedResponse = {
            'availableDates': json.loads(allAvailableBookingDatesJSON.content),
            'unconfirmedReservations': json.loads(allUnconfirmedReservationsJSON.content),
            'confirmedReservations': json.loads(allConfirmedReservationsJSON.content),
            'reservationsWithoutServiceProvider': json.loads(allReservationsWithoutServiceProviderJSON.content),
        }
        return JsonResponse(combinedResponse, safe=False)
    ic("Nie powinno nigdy miec miejsca")
    return redirect('index')


@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def addEditAvailableBookingDate(request):
    ic("Dodano/edytowano dostepny termin")
    if request.method == 'POST':
        ic(request.POST)
        responseData = {'status': 'success', 'message': 'Dostepny termin został dodany/edytowany.'}
        # title = request.POST.get('title')
        availableBookingDateIdSTR = request.POST.get('id')
        availableBookingDateId = int(availableBookingDateIdSTR)
        startTimeSTR = request.POST.get('startTime')
        endTimeSTR = request.POST.get('endTime')
        startDateSTR = request.POST.get('startDate')
        endDateSTR = request.POST.get('endDate')
        intervalTime = request.POST.get('intervalTime')
        breakBetweenIntervals = request.POST.get('breakBetweenIntervals')
        intervalTime = intervalTime if intervalTime != "" else None
        breakBetweenIntervals = breakBetweenIntervals if breakBetweenIntervals != "" else 0
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDateSTR, '%Y-%m-%d').date()
        start = datetime.combine(startDate, startTime)
        end = datetime.combine(endDate, endTime)
        currentUser = request.user
        try:
            if availableBookingDateId == -1:
                availableBookingDate = AvailableBookingDate(user=currentUser, start=start, end=end, intervalTime=intervalTime, breakBetweenIntervals=breakBetweenIntervals)
                availableBookingDate.save()
            else:
                availableBookingDate = AvailableBookingDate.objects.get(id=availableBookingDateId)
                # availableBookingDate.user = currentUser
                availableBookingDate.start = start
                availableBookingDate.end = end
                availableBookingDate.intervalTime = intervalTime
                availableBookingDate.breakBetweenIntervals = breakBetweenIntervals
                availableBookingDate.save()
                if availableBookingDate.intervalTime and int(availableBookingDate.intervalTime) > 0:
                    for reservation in availableBookingDate.reservation_set.filter(isAccepted=False):
                        if (reservation.end - reservation.start) != timedelta(minutes=(int(availableBookingDate.intervalTime)) + int(availableBookingDate.breakBetweenIntervals)):
                            reservation.availableBookingDate = None
                            reservation.save()
        except ValidationError as e:
            # messages.error(request, e.message)
            responseData = {'status': 'error', 'message': e.message}
        return JsonResponse(responseData)


@login_required(login_url='login')
def addEditReservation(request):
    ic("Dodaj/Edytuj rezerwacje")
    if request.method == 'POST':
        ic(request.POST)
        responseData = {'status': 'success', 'message': 'Rezerwacja została dodana/edytowana.'}
        startTimeSTR = request.POST.get('startTime')
        endTimeSTR = request.POST.get('endTime')
        startDateSTR = request.POST.get('startDate')
        endDateSTR = request.POST.get('endDate')
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDateSTR, '%Y-%m-%d').date()
        start = datetime.combine(startDate, startTime)
        end = datetime.combine(endDate, endTime)
        eventIdSTR = request.POST.get('id')
        eventId = int(eventIdSTR)
        eventTypeSTR = request.POST.get('eventType')
        eventType = int(eventTypeSTR)
        currentUser = request.user
        try:
            if eventType == 0:  # tworzenie nowej rezerwacji
                ic("tworzenie nowej rezerwacji")
                reservation = Reservation.objects.create(
                    bookingPerson=currentUser,
                    availableBookingDate=AvailableBookingDate.objects.get(pk=eventId),
                    start=start,
                    end=end,
                    isAccepted=False
                )
            if eventType == 1:  # edytowanie istniejacej rezerwacji
                ic("edytowanie istniejacej rezerwacji")
                reservation = Reservation.objects.get(pk=eventId)
                reservation.start = start
                reservation.end = end
                reservation.save()
            if eventType == 3:
                if eventId == -1:  # tworzenie nowej propozycji rezerwacji
                    ic("tworzenie nowej propozycji rezerwacji")
                    reservation = Reservation.objects.create(
                        bookingPerson=currentUser,
                        availableBookingDate= None,
                        start=start,
                        end=end,
                        isAccepted=False
                    )
                else:  # edytowanie propozycji rezerwacji
                    ic("edytowanie propozycji rezerwacji")
                    reservation = Reservation.objects.get(id=int(eventId))
                    # reservation.bookingPerson = currentUser
                    reservation.start = start
                    reservation.end = end
                    reservation.save()
        except ValidationError as e:
            responseData = {'status': 'error', 'message': e.message}
        return JsonResponse(responseData)


@login_required(login_url='login')
def deleteEvent(request):
    ic("Otrzymano prosbe o usuniecie")
    if request.method == 'POST':
        eventId = request.POST.get('id')
        eventTypeId = request.POST.get('eventTypeId')
        if int(eventTypeId) == 0:
            availableBookingDate = AvailableBookingDate.objects.get(pk=int(eventId))
            availableBookingDate.delete()
            ic("Usunieto dostepny termin")
        else:
            reservation = Reservation.objects.get(pk=int(eventId))
            reservation.delete()
            ic("Usunieto rezerwacje")
    return JsonResponse({'status': 'success', 'message': 'Usunieto.'})


@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def confirmOrRejectReservation(request):
    ic("Potwierdzono lub usunieto rezerwacje")
    if request.method == 'POST':
        ic(request.POST)
        responseData = {'status': 'success', 'message': 'Potwierdzono wydarzenie.'}
        reservationId = request.POST.get('id')
        reservation = Reservation.objects.get(pk=int(reservationId))
        action = request.POST.get('action')
        try:
            if action == 'confirmNew':
                newAvailableBookingDate = AvailableBookingDate.objects.create(
                    user=request.user,
                    start=reservation.start,
                    end=reservation.end,
                    intervalTime=None,
                    breakBetweenIntervals=0)
                reservation.availableBookingDate = newAvailableBookingDate
                reservation.isAccepted = True
                reservation.save()
            elif action == 'confirmExist':
                errorMessage = saveReservationWhichCouldBePartOfAvailableBookingData(reservation)
                if errorMessage:
                    messages.error(request, errorMessage)
            elif action == 'reject':
                reservation.delete()
        except ValidationError as e:
            ic("JEST ERROR?", e)
            responseData = {'status': 'error', 'message': e.message}
        return JsonResponse(responseData)


@login_required(login_url='login')
def dragEvent(request):
    ic("Przeciagnieto")
    if request.method == 'POST':
        ic(request.POST)
        responseData = {'status': 'success', 'message': 'Przeciagnieto wydarzenie.'}
        newStartString = request.POST.get('newStart')
        newEndString = request.POST.get('newEnd')
        newStartDate = datetime.strptime(newStartString, '%d/%m/%Y %H:%M')
        newEndDate = datetime.strptime(newEndString, '%d/%m/%Y %H:%M')
        eventIdString = request.POST.get('selectedDragEventId')
        eventId = int(eventIdString)
        eventTypeString = request.POST.get('eventType')
        eventType = int(eventTypeString)
        ic(newStartDate, newEndDate, eventId, eventType)
        try:
            if eventType == 0:
                availableBookingDate = AvailableBookingDate.objects.get(id=eventId)
                availableBookingDate.start = newStartDate
                availableBookingDate.end = newEndDate
                availableBookingDate.save()
            if eventType == 3 or eventType == 1:
                reservation = Reservation.objects.get(id=eventId)
                reservation.start = newStartDate
                reservation.end = newEndDate
                reservation.save()
        except ValidationError as e:
            ic("JEST ERROR?", e)
            responseData = {'status': 'error', 'message': e.message}
        return JsonResponse(responseData)


# @login_required(login_url='login')
# def reserve(request):
#     ic("Zarezerwowano")
#     if request.method == "POST":
#         ic(request.POST)
#         responseData = {'status': 'success', 'message': 'Rezerwacja została dodana/edytowana.'}
#         availableBookingDateId = request.POST.get('id')
#         ic(availableBookingDateId)
#         selectedAvailableBookingDate = AvailableBookingDate.objects.get(id=int(availableBookingDateId))
#         startTimeSTR = request.POST.get('startTime')
#         endTimeSTR = request.POST.get('endTime')
#         startDateSTR = request.POST.get('startDate')
#         endDateSTR = request.POST.get('endDate')
#         startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
#         endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
#         startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
#         endDate = datetime.strptime(endDateSTR, '%Y-%m-%d').date()
#         start = datetime.combine(startDate, startTime)
#         end = datetime.combine(endDate, endTime)
#         try:
#             reservation = Reservation.objects.create(
#                 bookingPerson=request.user,
#                 availableBookingDate=selectedAvailableBookingDate,
#                 start=start,
#                 end=end,
#                 isAccepted=False)
#         except ValidationError as e:
#             responseData = {'status': 'error', 'message': e.message}
#         return JsonResponse(responseData)


# @allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
# def deleteAvailableBookingDate(request):
#     ic("Usunieto dostepny termin")
#     if request.method == 'POST':
#         availableBookingDateId = request.POST.get('id')
#         ic(availableBookingDateId)
#         availableBookingDate = AvailableBookingDate.objects.get(pk=int(availableBookingDateId))
#         availableBookingDate.delete()
#
#
# @login_required(login_url='login')
# def deleteReservation(request):
#     ic("Usunieto rezerwacje")
#     if request.method == 'POST':
#         reservationId = request.POST.get('id')
#         ic(reservationId)
#         reservation = Reservation.objects.get(pk=int(reservationId))
#         reservation.delete()


@login_required(login_url='login')
def addDesiredReservationDate(request):
    ic("Dodaj dostepny termin")
    if request.method == 'POST':
        ic(request.POST)
        responseData = {'status': 'success', 'message': 'Propozycja została dodana/edytowana.'}
        startTimeSTR = request.POST.get('startTime')
        endTimeSTR = request.POST.get('endTime')
        startDateSTR = request.POST.get('startDate')
        endDateSTR = request.POST.get('endDate')
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDateSTR, '%Y-%m-%d').date()
        start = datetime.combine(startDate, startTime)
        end = datetime.combine(endDate, endTime)
        # currentUser = request.user
        try:
            reservation = Reservation.objects.create(
                bookingPerson=request.user,
                availableBookingDate=None,
                start=start,
                end=end,
                isAccepted=False)
        except ValidationError as e:
            ic(e)
            responseData = {'status': 'error', 'message': e.message}
        return JsonResponse(responseData)


@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def confirmDesiredReservationProposition(request):
    ic("Potwierdzono rezerwacje przyjeto termin")
    if request.method == 'POST':
        reservationId = request.POST.get('selectedReservationId')
        ic(reservationId)
        reservation = Reservation.objects.get(pk=reservationId)
        try:
            newAvailableBookingDate = AvailableBookingDate.objects.create(
                user=request.user,
                start=reservation.start,
                end=reservation.end,
                intervalTime=None,
                breakBetweenIntervals=0)
            reservation.availableBookingDate = newAvailableBookingDate
            reservation.isAccepted = True
            reservation.save()
        except ValidationError as e:
            messages.error(request, e.message)
    return redirect('index')


@login_required(login_url='login')
def reserveIntervalOfBookingDate(request):
    ic("Zarezerwowano przedzial")
    if request.method == "POST":
        availableBookingDateId = request.POST.get('selectedBookingDateId')
        startTime = request.POST.get('availableIntervalTimes')
        selectedAvailableBookingDate = AvailableBookingDate.objects.get(id=availableBookingDateId)
        start = datetime.strptime(startTime, '%d/%m/%Y %H:%M')
        end = start + timedelta(minutes=selectedAvailableBookingDate.intervalTime) + timedelta(minutes=selectedAvailableBookingDate.breakBetweenIntervals)
        try:
            reservation = Reservation.objects.create(
                bookingPerson=request.user,
                availableBookingDate=selectedAvailableBookingDate,
                start=start,
                end=end,
                isAccepted=False)
        except ValidationError as e:
            messages.error(request, e.message)
    return redirect('index')


@login_required(login_url='login')
def reservePartSingleDayBookingDate(request):
    ic("Zarezerwowano czesc dostepnego terminu z jednego dnia")
    if request.method == "POST":
        availableBookingDateId = request.POST.get('selectedBookingDateId')
        selectedAvailableBookingDate = AvailableBookingDate.objects.get(id=availableBookingDateId)
        startTimeSTR = request.POST.get('startTime')
        endTimeSTR = request.POST.get('endTime')
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        start = datetime.combine(selectedAvailableBookingDate.start.date(), startTime)
        end = datetime.combine(selectedAvailableBookingDate.end.date(), endTime)
        ic(startTimeSTR, endTimeSTR)
        try:
            reservation = Reservation.objects.create(
                bookingPerson=request.user,
                availableBookingDate=selectedAvailableBookingDate,
                start=start,
                end=end,
                isAccepted=False)
        except ValidationError as e:
            messages.error(request, e.message)
    ic("DZIALA")
    return redirect('index')


@login_required(login_url='login')
def reservePartMultipleDaysBookingDate(request):
    ic("Zarezerwowano czesc dostepnego terminu z wielu dni")
    if request.method == "POST":
        availableBookingDateId = request.POST.get('selectedBookingDateId')
        ic(availableBookingDateId)
        selectedAvailableBookingDate = AvailableBookingDate.objects.get(id=availableBookingDateId)
        startTimeSTR = request.POST.get('startTime')
        endTimeSTR = request.POST.get('endTime')
        startDateSTR = request.POST.get('startDate')
        endDateSTR = request.POST.get('endDate')
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDateSTR, '%Y-%m-%d').date()
        start = datetime.combine(startDate, startTime)
        end = datetime.combine(endDate, endTime)
        try:
            reservation = Reservation.objects.create(
                bookingPerson=request.user,
                availableBookingDate=selectedAvailableBookingDate,
                start=start,
                end=end,
                isAccepted=False)
        except ValidationError as e:
            messages.error(request, e.message)
    return redirect('index')


@login_required(login_url='login')
def reserveEntireBookingDate(request):
    ic("Zarezerwowano dostepny termin")
    if request.method == 'POST':
        availableBookingDateId = request.POST.get('selectedBookingDateId')
        availableBookingDateStart = request.POST.get('selectedBookingDateStart')
        availableBookingDateEnd = request.POST.get('selectedBookingDateEnd')
        startDatetime = datetime.fromisoformat(availableBookingDateStart[:-1])
        endDatetime = datetime.fromisoformat(availableBookingDateEnd[:-1])
        ic(availableBookingDateStart, startDatetime)
        selectedAvailableBookingDate = AvailableBookingDate.objects.get(pk=availableBookingDateId)
        try:
            reservation = Reservation.objects.create(
                bookingPerson=request.user,
                availableBookingDate=selectedAvailableBookingDate,
                start=startDatetime,
                end=endDatetime,
                isAccepted=False)
        except ValidationError as e:
            messages.error(request, e.message)
    return redirect('index')



@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def addAvailableBookingDateByCalendar(request):
    ic("Dodano event")
    if request.method == 'POST':
        ic(request.POST)
        # title = request.POST.get('title')
        startTimeSTR = request.POST.get('startTime')
        endTimeSTR = request.POST.get('endTime')
        startDateSTR = request.POST.get('startStr')
        endDateSTR = request.POST.get('endStr')
        intervalTime = request.POST.get('intervalTime')
        breakBetweenIntervals = request.POST.get('breakBetweenIntervals')
        intervalTime = intervalTime if intervalTime != "" else None
        breakBetweenIntervals = breakBetweenIntervals if breakBetweenIntervals != "" else 0
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDateSTR, '%Y-%m-%d').date()
        start = datetime.combine(startDate, startTime)
        end = datetime.combine(endDate, endTime)
        currentUser = request.user
        availableBookingDate = AvailableBookingDate(user=currentUser, start=start, end=end, intervalTime=intervalTime, breakBetweenIntervals=breakBetweenIntervals)
        try:
            availableBookingDate.save()
        except ValidationError as e:
            messages.error(request, e.message)
    return redirect('index')


@login_required(login_url='login')
def addDesiredReservationDateByCalendar(request):
    ic("Dodano pozadany czas rezerwacji")
    if request.method == 'POST':
        ic(request.POST)
        # title = request.POST.get('title')
        startTimeSTR = request.POST.get('startTime')
        endTimeSTR = request.POST.get('endTime')
        startDateSTR = request.POST.get('startStr')
        endDateSTR = request.POST.get('endStr')
        ic(startTimeSTR, endTimeSTR, startDateSTR, endDateSTR)
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDateSTR, '%Y-%m-%d').date()
        start = datetime.combine(startDate, startTime)
        end = datetime.combine(endDate, endTime)
        currentUser = request.user
        # availableBookingDate = AvailableBookingDate(user=currentUser, start=start, end=end, intervalTime=intervalTime,
        #                                             breakBetweenIntervals=breakBetweenIntervals)
        reservation = Reservation(bookingPerson=currentUser, availableBookingDate=None, start=start, end=end, isAccepted=False)
        try:
            reservation.save()
        except ValidationError as e:
            messages.error(request, e.message)

    return redirect('index')


@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def addAvailableBookingDate(request):
    ic("Dodano dostepny termin")
    if request.method == 'POST':
        ic(request.POST)
        # title = request.POST.get('title')
        startTimeSTR = request.POST.get('startTime')
        endTimeSTR = request.POST.get('endTime')
        startDateSTR = request.POST.get('startDate')
        endDateSTR = request.POST.get('endDate')
        intervalTime = request.POST.get('intervalTime')
        breakBetweenIntervals = request.POST.get('breakBetweenIntervals')
        intervalTime = intervalTime if intervalTime != "" else None
        breakBetweenIntervals = breakBetweenIntervals if breakBetweenIntervals != "" else 0
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDateSTR, '%Y-%m-%d').date()
        start = datetime.combine(startDate, startTime)
        end = datetime.combine(endDate, endTime)
        currentUser = request.user
        availableBookingDate = AvailableBookingDate(user=currentUser, start=start, end=end, intervalTime=intervalTime, breakBetweenIntervals=breakBetweenIntervals)
        try:
            availableBookingDate.save()
        except ValidationError as e:
            messages.error(request, e.message)
    return redirect('index')


@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def editAvailableBookingDate(request):
    ic("Edytuj dostepny termin")
    if request.method == 'POST':
        # title = request.POST.get('title')
        startTimeSTR = request.POST.get('startTime')
        endTimeSTR = request.POST.get('endTime')
        startDateSTR = request.POST.get('startDate')
        endDateSTR = request.POST.get('endDate')
        intervalTime = request.POST.get('intervalTime')
        breakBetweenIntervals = request.POST.get('breakBetweenIntervals')
        intervalTime = intervalTime if intervalTime != "" else None
        breakBetweenIntervals = breakBetweenIntervals if breakBetweenIntervals != "" else 0
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDateSTR, '%Y-%m-%d').date()
        start = datetime.combine(startDate, startTime)
        end = datetime.combine(endDate, endTime)
        ic(startTimeSTR, endTimeSTR)
        # currentUser = request.user
        availableBookingDateId = request.POST.get('selectedEvent')
        availableBookingDate = AvailableBookingDate.objects.get(id=availableBookingDateId)
        # availableBookingDate.user = currentUser
        availableBookingDate.start = start
        availableBookingDate.end = end
        availableBookingDate.intervalTime = intervalTime
        availableBookingDate.breakBetweenIntervals = breakBetweenIntervals
        try:
            availableBookingDate.save()
            if availableBookingDate.intervalTime and int(availableBookingDate.intervalTime) > 0:
                for reservation in availableBookingDate.reservation_set.filter(isAccepted=False):
                    if (reservation.end - reservation.start) != timedelta(minutes=(int(availableBookingDate.intervalTime)) + int(availableBookingDate.breakBetweenIntervals)):
                        reservation.availableBookingDate = None
                        reservation.save()
        except ValidationError as e:
            messages.error(request, e.message)
    ic("DZIALA")
    return redirect('index')


@login_required(login_url='login')
def editDesiredReservationDate(request):
    ic("Edytuj dostepny termin")
    if request.method == 'POST':
        # title = request.POST.get('title')
        startTimeSTR = request.POST.get('startTime')
        endTimeSTR = request.POST.get('endTime')
        startDateSTR = request.POST.get('startDate')
        endDateSTR = request.POST.get('endDate')
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDateSTR, '%Y-%m-%d').date()
        start = datetime.combine(startDate, startTime)
        end = datetime.combine(endDate, endTime)
        ic(startTimeSTR, endTimeSTR)
        # currentUser = request.user
        reservationId = request.POST.get('selectedEvent')
        reservation = Reservation.objects.get(id=reservationId)
        # reservation.user = currentUser
        reservation.start = start
        reservation.end = end
        try:
            reservation.save()
        except ValidationError as e:
            messages.error(request, e.message)
    ic("DZIALA")
    return redirect('index')


@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def notForClients(request):
    return render(request, 'calendar/restricted.html')


@login_required(login_url='login')
def userProfile(request, pk):
    userOwnerOfProfile = User.objects.get(pk=pk)
    userProfileInstance = UserProfile.objects.get(user=userOwnerOfProfile)
    return render(request, 'accounts/userProfile.html', {"userProfile": userProfileInstance})


@login_required(login_url='login')
def updateUser(request):
    if request.method == 'POST':
        userForm = UpdateUserForm(request.POST, instance=request.user)
        profileForm = UpdateProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if userForm.is_valid() and profileForm.is_valid():
            userForm.save()
            profileForm.save()
            return redirect('userProfile', pk=request.user.id)
    else:
        userForm = UpdateUserForm(instance=request.user)
        profileForm = UpdateProfileForm(instance=request.user.userprofile)
    userOwnerOfProfile = User.objects.get(pk=request.user.id)
    userProfileInstance = UserProfile.objects.get(user=userOwnerOfProfile)
    return render(request, 'accounts/updateUser.html', {"userProfile": userProfileInstance, 'userForm': userForm, 'profileForm': profileForm})


@unauthenticatedUser
def registerUser(request):
    form = CreateUserForm()  # it's for case of not post or wrong validation
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            clientGroup = Group.objects.get(name='client')
            user.groups.add(clientGroup)
            username = form.cleaned_data.get('username')
            messages.success(request, 'Konto zostało utworzone dla: ' + username)
            # return redirect('login')
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    return render(request, 'accounts/register.html', {'form': form})


# @unauthenticatedUser
# def loginUser(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             if 'next' in request.POST:
#                 return redirect(request.POST['next'])
#             return redirect('index')
#         else:
#             messages.info(request, 'Username or password is incorrect')
#     context = {}
#     return render(request, 'accounts/login.html', context)

@unauthenticatedUser
def loginUser(request):
    errors = []
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if 'next' in request.POST:
                    return redirect(request.POST['next'])
                return redirect('index')
        else:
            errors.append('Username or password is incorrect')
            # messages.error(request, 'Username or password is incorrect')
    return render(request, 'accounts/login.html', {'form': form, 'errors': errors})


def logoutUser(request):
    theme = True if 'is_dark_theme' in request.session else False
    logout(request)
    if theme:
        request.session["is_dark_theme"] = True
    return redirect('index')



# TESTY
def myTest(request):
    return render(request, 'test/myTest.html')
# Wersja testowa THEME
from django.views.generic import ListView, DetailView

class PostListView(ListView):
    model = Post
    template_name = 'test/posts/main.html'

class PostDetailView(DetailView):
    model = Post
    template_name = 'test/posts/detail.html'
