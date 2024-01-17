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
from django.db.models import Q, F, Prefetch, Count, Sum, ExpressionWrapper, F, DurationField, OuterRef, Subquery
from django.db import connection, reset_queries


def calendar(request):
    serviceProviders = User.objects.filter(availablebookingdate__isnull=False, availablebookingdate__isDeleted=False).distinct().prefetch_related('userprofile')
    serviceProvidersWithImages = []
    for serviceProvider in serviceProviders:
        userProfileObject = serviceProvider.userprofile  # UserProfile.objects.get(user=serviceProvider)
        profileImageUrl = userProfileObject.profileImage.url if userProfileObject and userProfileObject.profileImage else None
        serviceProvidersWithImages.append((serviceProvider, profileImageUrl))

    clientGroup = Group.objects.get(name='client')
    clients = User.objects.filter(groups=clientGroup).prefetch_related('userprofile')
    clientsWithImages = []
    for client in clients:
        clientProfile = client.userprofile # UserProfile.objects.get(user=client)
        clientProfileUrl = clientProfile.profileImage.url if clientProfile and clientProfile.profileImage else None
        clientsWithImages.append((client, clientProfileUrl))

    context = {
        'serviceProvidersWithImages': serviceProvidersWithImages,
        'clientsWithImages': clientsWithImages,
        'rangeFrom15to180increasesBy15': geRangeTimeStrings(15, 180, 15),
    }
    return render(request, 'calendar/calendar.html', context)


def allReservationsWithoutServiceProvider(request, allClients=True, selectedClientsIds=None):
    if allClients:
        reservations = Reservation.objects.filter(availableBookingDate__isnull=True, isDeleted=False).select_related('bookingPerson', 'availableBookingDate', 'availableBookingDate__user')
    else:
        reservations = Reservation.objects.filter(availableBookingDate__isnull=True, isDeleted=False, bookingPerson__id__in=selectedClientsIds).select_related('bookingPerson', 'availableBookingDate', 'availableBookingDate__user')
    out = []
    for reservation in reservations:
        out.append(getReservationWithoutServiceProviderJsonData(reservation))
    return JsonResponse(out, safe=False)


def allUnconfirmedReservations(request, allClients=True, selectedClientsIds=None):
    if allClients:
        reservations = Reservation.objects.filter(isAccepted=False, availableBookingDate__isnull=False, availableBookingDate__isDeleted=False, isDeleted=False).select_related('bookingPerson', 'availableBookingDate', 'availableBookingDate__user')
    else:
        reservations = Reservation.objects.filter(isAccepted=False, availableBookingDate__isnull=False, availableBookingDate__isDeleted=False, isDeleted=False, bookingPerson__id__in=selectedClientsIds).select_related('bookingPerson', 'availableBookingDate', 'availableBookingDate__user')
    out = []
    for reservation in reservations:
        out.append(getUnconfirmedReservationJsonData(reservation))
    return JsonResponse(out, safe=False)


def allConfirmedReservations(request, allUsers=True, selectedServiceProvidersIds=None, selectedClientsIds=None):
    if allUsers:
        reservations = Reservation.objects.filter(isAccepted=True, isDeleted=False).select_related('bookingPerson', 'availableBookingDate', 'availableBookingDate__user')
    else:
        reservations = Reservation.objects.filter(
            Q(isAccepted=True, isDeleted=False, availableBookingDate__user__id__in=selectedServiceProvidersIds) |
            Q(isAccepted=True, isDeleted=False, bookingPerson__id__in=selectedClientsIds)
        ).select_related('bookingPerson', 'availableBookingDate', 'availableBookingDate__user')
    out = []
    for reservation in reservations:
        out.append(getConfirmedReservationJsonData(reservation))
    return JsonResponse(out, safe=False)


def allAvailableBookingDates(request, allServiceProviders=True, selectedServiceProvidersIds=None):
    if allServiceProviders:
        availableBookingDates = AvailableBookingDate.objects.filter(isDeleted=False)\
            .prefetch_related('user', Prefetch('reservation_set', queryset=Reservation.objects.filter(isAccepted=True, isDeleted=False).order_by('start'), to_attr='acceptedReservations'))
    else:
        availableBookingDates = AvailableBookingDate.objects.filter(isDeleted=False, user__id__in=selectedServiceProvidersIds)\
            .prefetch_related('user', Prefetch('reservation_set', queryset=Reservation.objects.filter(isAccepted=True, isDeleted=False).order_by('start'), to_attr='acceptedReservations'))
    out = []
    for availableBookingDate in availableBookingDates:
        freeTimesInAvailableBookingDate = getAvailableTimeRanges(availableBookingDate)
        for freeTime in freeTimesInAvailableBookingDate:
            possibleDragging = True if availableBookingDate.acceptedReservations.count == 0 else False
            out.append(getAvailableBookingDateJsonData(availableBookingDate, freeTime, possibleDragging))
    return JsonResponse(out, safe=False)


def filterServiceProviders(request):
    if request.method == 'POST':
        ic(request.POST)
        selectedServiceProvidersJSON = request.POST.get('selectedServiceProviders')
        selectedServiceProviders = json.loads(selectedServiceProvidersJSON)
        selectedClientsJSON = request.POST.get('selectedClients')
        selectedClients = json.loads(selectedClientsJSON)
        selectedServiceProvidersIds = [option for option in selectedServiceProviders]
        if len(selectedServiceProvidersIds) == 0:
            selectedServiceProvidersIds = User.objects.values_list('id', flat=True)
        selectedClientsIds = [option for option in selectedClients]
        if len(selectedClientsIds) == 0:
            selectedClientsIds = User.objects.values_list('id', flat=True)
        ic(selectedServiceProvidersIds, selectedClientsIds)
        allAvailableBookingDatesJSON = allAvailableBookingDates(request, allServiceProviders=False, selectedServiceProvidersIds=selectedServiceProvidersIds)
        allUnconfirmedReservationsJSON = allUnconfirmedReservations(request, allClients=False, selectedClientsIds=selectedClientsIds)
        allConfirmedReservationsJSON = allConfirmedReservations(request, allUsers=False, selectedServiceProvidersIds=selectedServiceProvidersIds, selectedClientsIds=selectedClientsIds)
        allReservationsWithoutServiceProviderJSON = allReservationsWithoutServiceProvider(request, allClients=False, selectedClientsIds=selectedClientsIds)
        combinedResponse = {
            'availableDates': json.loads(allAvailableBookingDatesJSON.content),
            'unconfirmedReservations': json.loads(allUnconfirmedReservationsJSON.content),
            'confirmedReservations': json.loads(allConfirmedReservationsJSON.content),
            'reservationsWithoutServiceProvider': json.loads(allReservationsWithoutServiceProviderJSON.content),
        }
        return JsonResponse(combinedResponse, safe=False)


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
                availableBookingDate.save(fromUser=request.user)
            else:
                availableBookingDate = AvailableBookingDate.objects.get(id=availableBookingDateId)
                # availableBookingDate.user = currentUser
                availableBookingDate.start = start
                availableBookingDate.end = end
                availableBookingDate.intervalTime = intervalTime
                availableBookingDate.breakBetweenIntervals = breakBetweenIntervals
                availableBookingDate.save(fromUser=request.user)
                if currentUser != availableBookingDate.user:
                    print(f"{currentUser} zmienił dostepny termin uzytkownika {availableBookingDate.user}")
                    createNotificationAndSendMail(7, availableBookingDate.user, currentUser, availableBookingDate, None)
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
                )
                createNotificationAndSendMail(2, reservation.availableBookingDate.user, currentUser, reservation.availableBookingDate, reservation)
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
                    )
                else:  # edytowanie propozycji rezerwacji
                    ic("edytowanie propozycji rezerwacji")
                    reservation = Reservation.objects.get(id=int(eventId))
                    # reservation.bookingPerson = currentUser
                    reservation.start = start
                    reservation.end = end
                    reservation.save()
                    if currentUser != reservation.bookingPerson:
                        print(f"{currentUser} edytował propozycje terminu uzytkownika {reservation.bookingPerson}")
                        createNotificationAndSendMail(8, reservation.bookingPerson, currentUser, None, reservation)
        except ValidationError as e:
            responseData = {'status': 'error', 'message': e.message}
        return JsonResponse(responseData)


@login_required(login_url='login')
def deleteEvent(request):
    ic("Otrzymano prosbe o usuniecie")
    if request.method == 'POST':
        eventId = request.POST.get('id')
        eventTypeId = request.POST.get('eventTypeId')
        currentUser = request.user
        if int(eventTypeId) == 0:
            availableBookingDate = AvailableBookingDate.objects.get(pk=int(eventId))
            availableBookingDate.isDeleted = True
            availableBookingDate.save(fromUser=request.user)
            ic("Usunieto dostepny termin")
            if currentUser != availableBookingDate.user:
                print(f"{currentUser} usunal dostepny termin uzytkownika {availableBookingDate.user}")
                createNotificationAndSendMail(6, availableBookingDate.user, currentUser, availableBookingDate, None)
        else:
            reservation = Reservation.objects.get(pk=int(eventId))
            reservation.isDeleted = True
            reservation.save()
            ic("Usunieto rezerwacje")
            if currentUser != reservation.bookingPerson:
                if int(eventTypeId) == 1:
                    print(f"{currentUser} usunal rezerwacje uzytkownika {reservation.bookingPerson}")
                    createNotificationAndSendMail(4, reservation.bookingPerson, currentUser, None, reservation)
                elif int(eventTypeId) == 2:
                    print(f"{currentUser} usunal potwierdzony termin dotyczacy {reservation.bookingPerson} i {reservation.availableBookingDate.user} wywolane bo currentUser != klienta")
                    createNotificationAndSendMail(3, reservation.bookingPerson, currentUser, reservation.availableBookingDate, reservation)
                elif int(eventTypeId) == 3:
                    print(f"{currentUser} usunal propozycje terminu uzytkownika {reservation.bookingPerson}")
                    createNotificationAndSendMail(5, reservation.bookingPerson, currentUser, None, reservation)
                else:
                    raise Exception(f"To nie powinno sie wydarzyc. eventType = {eventTypeId}")
            elif int(eventTypeId) == 2 and reservation.availableBookingDate.user != currentUser:
                print(f"{currentUser} usunal potwierdzony termin dotyczacy {reservation.bookingPerson} i {reservation.availableBookingDate.user} wywolane bo currentUser != uslugodawcy")
                createNotificationAndSendMail(3, reservation.availableBookingDate.user, currentUser, reservation.availableBookingDate, reservation)
    return JsonResponse({'status': 'success', 'message': 'Usunieto.'})


@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def confirmOrRejectReservation(request):
    ic("Potwierdzono lub usunieto rezerwacje")
    if request.method == 'POST':
        ic(request.POST)
        responseData = {'status': 'success', 'message': 'Potwierdzono wydarzenie.'}
        reservationId = request.POST.get('id')
        reservation = Reservation.objects.filter(pk=int(reservationId)).select_related("bookingPerson", "availableBookingDate", "availableBookingDate__user").first()
        action = request.POST.get('action')
        userWhoConfirmedReservation = request.user
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
                createNotificationAndSendMail(1, reservation.bookingPerson, userWhoConfirmedReservation, None, reservation)
            elif action == 'confirmExist':
                errorMessage = saveReservationWhichCouldBePartOfAvailableBookingData(reservation, userWhoConfirmedReservation)
                if errorMessage:
                    #messages.error(request, errorMessage)
                    responseData = {'status': 'error', 'message': errorMessage}
            elif action == 'reject':
                reservation.isDeleted = True
                reservation.save()
                createNotificationAndSendMail(4, reservation.bookingPerson, userWhoConfirmedReservation, None, reservation)
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
        currentUser = request.user
        try:
            if eventType == 0:
                availableBookingDate = AvailableBookingDate.objects.get(id=eventId)
                availableBookingDate.start = newStartDate
                availableBookingDate.end = newEndDate
                availableBookingDate.save(fromUser=request.user)
                if currentUser != availableBookingDate.user:
                    print(f"{currentUser} zmienił dostepny termin uzytkownika {availableBookingDate.user}")
                    createNotificationAndSendMail(7, availableBookingDate.user, currentUser, availableBookingDate, None)
            if eventType == 3 or eventType == 1:
                reservation = Reservation.objects.get(id=eventId)
                reservation.start = newStartDate
                reservation.end = newEndDate
                reservation.save()
                if currentUser != reservation.bookingPerson and eventType == 3:
                    print(f"{currentUser} edytował propozycje terminu uzytkownika {reservation.bookingPerson}")
                    createNotificationAndSendMail(8, reservation.bookingPerson, currentUser, None, reservation)
        except ValidationError as e:
            ic("JEST ERROR?", e)
            responseData = {'status': 'error', 'message': e.message}
        return JsonResponse(responseData)


def readNotification(request):
    if request.method == 'POST':
        ic(request.POST)
        try:
            responseData = {'status': 'successWithoutNeedToRefetch', 'message': 'Przeczytano powiadomienie.'}
            notificationId = request.POST.get('id')
            notification = Notification.objects.get(pk=int(notificationId))
            notification.hasBeenSeen = True
            notification.save()
        except ValidationError as e:
            ic("Wystąpił błąd: ", e)
            responseData = {'status': 'error', 'message': e.message}
        return JsonResponse(responseData)


def eventTable(request):
    filteredAvailableBookingDates = AvailableBookingDate.objects.filter(isDeleted=False).exclude(reservation__isDeleted=False, reservation__isAccepted=True).distinct()
    reservations = Reservation.objects.filter(isDeleted=False).select_related('bookingPerson', 'availableBookingDate', 'availableBookingDate__user')
    reservationsWithJsonData = []
    for reservation in reservations:
        if reservation.availableBookingDate is None:
            reservationJsonData = getReservationWithoutServiceProviderJsonData(reservation)
        elif reservation.isAccepted:
            reservationJsonData = getConfirmedReservationJsonData(reservation)
        else:
            reservationJsonData = getUnconfirmedReservationJsonData(reservation)
        reservationsWithJsonData.append({'reservationObject': reservation, 'jsonData': reservationJsonData})
    context = {'availableBookingDates': filteredAvailableBookingDates,
               'reservations': reservationsWithJsonData}
    return render(request, 'eventTable/eventTable.html', context)


def createStatistics(request):
    ic("Stworz statystyki")

    reset_queries()

    # Wersja uniwersalna gdzie dostaje sie uzytkownikow i ich dostepnego terminy
    # serviceProviderGroup = Group.objects.get(name='serviceProvider')
    # serviceProviders = User.objects.filter(groups=serviceProviderGroup).prefetch_related('availablebookingdate_set', 'availablebookingdate_set__reservation_set')
    # #ic(serviceProviders)
    # for serviceProvider in serviceProviders:
    #     for availableBookingDate in serviceProvider.availablebookingdate_set.all():
    #         ic(serviceProvider, availableBookingDate)


    # Suma wszystkich długości
    # serviceProviderGroup = Group.objects.get(name='serviceProvider')
    # serviceProviders = User.objects.filter(groups=serviceProviderGroup)  # .aggregate(Count('availablebookingdate'), Sum('availablebookingdate__id'))
    # ic(serviceProviders)
    # totalTimeSum = AvailableBookingDate.objects.filter(user__in=serviceProviders, isDeleted=False).aggregate(
    #     totalTimeSeconds=Sum(F('end') - F('start'), output_field=models.DurationField())
    # )
    # totalTimeSumHours = totalTimeSum['totalTimeSeconds'].total_seconds() / 3600
    # ic(totalTimeSumHours)



    # serviceProviderGroup = Group.objects.get(name='serviceProvider')
    # serviceProviders = User.objects.filter(groups=serviceProviderGroup).prefetch_related(
    #     Prefetch('availablebookingdate_set',
    #              queryset=AvailableBookingDate.objects.filter(isDeleted=False)
    #              .annotate(totalTimeSeconds=ExpressionWrapper(F('end') - F('start'), output_field=DurationField()))
    #              .filter(user=F('user'))
    #              .annotate(totalTime=Sum('totalTimeSeconds')),
    #              to_attr='totalTime')
    # )
    # ic(serviceProviders)
    # for serviceProvider in serviceProviders:
    #     ic(serviceProvider.username)
    #     for available_booking_date in serviceProvider.totalTime:
    #         ic(available_booking_date.totalTimeSeconds)
    #         ic(available_booking_date.totalTime)

    # Wersja co zwraca dla każdego dostepnego terminu czas jego trwania
    # serviceProviderGroup = Group.objects.get(name='serviceProvider')
    # serviceProviders = User.objects.filter(groups=serviceProviderGroup).prefetch_related(
    #     Prefetch('availablebookingdate_set',
    #              queryset=AvailableBookingDate.objects.filter(isDeleted=False)
    #              .annotate(availableBookingDateTimeSeconds=ExpressionWrapper(F('end') - F('start'), output_field=DurationField()))
    #              .filter(user=F('user')))
    # )
    # ic(serviceProviders)
    # for serviceProvider in serviceProviders:
    #     ic(serviceProvider.username)
    #     for available_booking_date in serviceProvider.availablebookingdate_set.all():
    #         ic(available_booking_date.availableBookingDateTimeSeconds)

    # Najlepsza wersja co zwraca już gotowy wynik
    totalTimeSubQuery = AvailableBookingDate.objects.filter(isDeleted=False, user=OuterRef('id'))\
        .annotate(availableBookingDateTimeSeconds=ExpressionWrapper(F('end') - F('start'), output_field=DurationField()))

    serviceProviderGroup = Group.objects.get(name='serviceProvider')
    serviceProviders = User.objects.filter(groups=serviceProviderGroup)\
        .annotate(totalAvailableTime=Subquery(totalTimeSubQuery.values('user').annotate(totalSum=Sum('availableBookingDateTimeSeconds')).values('totalSum')[:1]))

    for serviceProvider in serviceProviders:
        ic(serviceProvider.username)
        time = serviceProvider.totalAvailableTime.total_seconds() / 3600 if serviceProvider.totalAvailableTime is not None else 0
        ic(time)

    # totalTimeSubQuery = AvailableBookingDate.objects.filter(isDeleted=False, user=OuterRef('id')) \
    #     .annotate(
    #     availableBookingDateTimeSeconds=ExpressionWrapper(F('end') - F('start'), output_field=DurationField()))
    # serviceProviderGroup = Group.objects.get(name='serviceProvider')
    # serviceProviders = User.objects.filter(groups=serviceProviderGroup) \
    #     .annotate(totalAvailableTime=Subquery(totalTimeSubQuery.values('user').annotate(total=Sum('availableBookingDateTimeSeconds')).values('total')[:1]),
    #               numberOfAvailableTime=Subquery(totalTimeSubQuery.values('user').annotate(total=Count('availableBookingDateTimeSeconds')).values('total')[:1]))
    #
    # for serviceProvider in serviceProviders:
    #     ic(serviceProvider.username, serviceProvider.numberOfAvailableTime)
    #     time = serviceProvider.totalAvailableTime.total_seconds() / 3600 if serviceProvider.totalAvailableTime is not None else 0
    #     ic(time)

    # Wersja zwraca właściwy wynik, ale tylko dla usługodawców co mają conajmniej jeden dostępny termin
    # serviceProviderGroup = Group.objects.get(name='serviceProvider')
    # result = AvailableBookingDate.objects.filter(isDeleted=False, user__groups=serviceProviderGroup).values('user').annotate(total=Sum(ExpressionWrapper(F('end') - F('start'), output_field=DurationField())))
    # ic(result)
    # for serviceProviderWithTime in result:
    #     ic(serviceProviderWithTime['user__username'])
    #     time = serviceProviderWithTime['total'].total_seconds() / 3600 if serviceProviderWithTime['total'] is not None else 0
    #     ic(time)

    for query in connection.queries:
        ic(query['sql'], "\n")
    ic(len(connection.queries))

    # clientGroup = Group.objects.get(name='client')
    # clients = User.objects.filter(groups=clientGroup)
    return redirect('calendar')


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
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Konto zostało utworzone dla: ' + username)
            return redirect('calendar')
    return render(request, 'accounts/register.html', {'form': form})


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
                return redirect('calendar')
        else:
            errors.append('Username or password is incorrect')
    return render(request, 'accounts/login.html', {'form': form, 'errors': errors})


def logoutUser(request):
    theme = True if 'is_dark_theme' in request.session else False
    logout(request)
    if theme:
        request.session["is_dark_theme"] = True
    return redirect('calendar')


def deleteNotification(request):
    ic("Usunieto powiadomienie")
    if request.method == 'POST':
        ic(request.POST)
        responseData = {'status': 'successWithoutNeedToRefetch', 'message': 'Usunieto powiadomienie.'}
        notificationId = request.POST.get('id')
        notification = Notification.objects.get(pk=int(notificationId))
        notification.isDeleted = True
        notification.save()
        return JsonResponse(responseData)



# WIDOK TESTOWY
def myTest(request):
    availableBookingDates = AvailableBookingDate.objects.filter(isDeleted=False)
    filteredAvailableBookingDates = []
    for availableBookingDate in availableBookingDates:
        if availableBookingDate.reservation_set.filter(isAccepted=True, isDeleted=False).count() == 0:
            filteredAvailableBookingDates.append(availableBookingDate)
    reservations = Reservation.objects.filter(isDeleted=False)
    context = {'availableBookingDates': filteredAvailableBookingDates,
               'reservations': reservations}

    # serviceProviderGroup = Group.objects.get(name='serviceProvider')
    # serviceProviders = User.objects.filter(groups=serviceProviderGroup).prefetch_related('availablebookingdate_set', 'availablebookingdate_set__reservation_set')
    # context = {'serviceProviders': serviceProviders}
    return render(request, 'test/myTest.html', context)
# Wersja testowa THEME
from django.views.generic import ListView, DetailView

class PostListView(ListView):
    model = Post
    template_name = 'test/posts/main.html'

class PostDetailView(DetailView):
    model = Post
    template_name = 'test/posts/detail.html'
