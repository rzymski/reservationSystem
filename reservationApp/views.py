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
from django.db.models import Q
from django.db.models import Min, Max


def calendar(request):
    serviceProviders = User.objects.filter(availablebookingdate__isnull=False, availablebookingdate__isDeleted=False).distinct()
    serviceProvidersWithImages = []
    for serviceProvider in serviceProviders:
        userProfileObject = UserProfile.objects.get(user=serviceProvider)
        profileImageUrl = userProfileObject.profileImage.url if userProfileObject and userProfileObject.profileImage else None
        serviceProvidersWithImages.append((serviceProvider, profileImageUrl))

    clientGroup = Group.objects.get(name='client')
    clients = User.objects.filter(groups=clientGroup)
    clientsWithImages = []
    for client in clients:
        clientProfile = UserProfile.objects.get(user=client)
        clientProfileUrl = clientProfile.profileImage.url if clientProfile and clientProfile.profileImage else None
        clientsWithImages.append((client, clientProfileUrl))

    context = {
        'serviceProvidersWithImages': serviceProvidersWithImages,
        'clientsWithImages': clientsWithImages,
        'rangeFrom15to180increasesBy15': geRangeTimeStrings(15, 180, 15),
    }
    return render(request, 'calendar/calendar.html', context)


def allReservationsWithoutServiceProvider(request, allClients=True, selectedClientsIds=None):
    reservations = Reservation.objects.filter(availableBookingDate__isnull=True, isDeleted=False) if allClients else Reservation.objects.filter(availableBookingDate__isnull=True, isDeleted=False, bookingPerson__id__in=selectedClientsIds)
    out = []
    for reservation in reservations:
        out.append(getReservationWithoutServiceProviderJsonData(reservation))
    return JsonResponse(out, safe=False)


def allUnconfirmedReservations(request, allClients=True, selectedClientsIds=None):
    reservations = Reservation.objects.filter(isAccepted=False, availableBookingDate__isnull=False, availableBookingDate__isDeleted=False, isDeleted=False) if allClients else Reservation.objects.filter(isAccepted=False, availableBookingDate__isnull=False, availableBookingDate__isDeleted=False, isDeleted=False, bookingPerson__id__in=selectedClientsIds)
    out = []
    for reservation in reservations:
        out.append(getUnconfirmedReservationJsonData(reservation))
    return JsonResponse(out, safe=False)


def allConfirmedReservations(request, allUsers=True, selectedServiceProvidersIds=None, selectedClientsIds=None):
    if allUsers:
        reservations = Reservation.objects.filter(isAccepted=True, isDeleted=False)
    else:
        reservations = Reservation.objects.filter(
            Q(isAccepted=True, isDeleted=False, availableBookingDate__user__id__in=selectedServiceProvidersIds) |
            Q(isAccepted=True, isDeleted=False, bookingPerson__id__in=selectedClientsIds)
        )
    out = []
    for reservation in reservations:
        out.append(getConfirmedReservationJsonData(reservation))
    return JsonResponse(out, safe=False)


def allAvailableBookingDates(request, allServiceProviders=True, selectedServiceProvidersIds=None):
    availableBookingDates = AvailableBookingDate.objects.filter(isDeleted=False) if allServiceProviders else AvailableBookingDate.objects.filter(isDeleted=False, user__id__in=selectedServiceProvidersIds)
    out = []
    for availableBookingDate in availableBookingDates:
        freeTimesInAvailableBookingDate = getAvailableTimeRanges(availableBookingDate)
        for freeTime in freeTimesInAvailableBookingDate:
            possibleDragging = True if Reservation.objects.filter(isAccepted=True, availableBookingDate=availableBookingDate, isDeleted=False).count() == 0 else False
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
        reservation = Reservation.objects.get(pk=int(reservationId))
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
                    messages.error(request, errorMessage)
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
    ic("Przeczytano powiadomienie")
    if request.method == 'POST':
        ic(request.POST)
        responseData = {'status': 'successWithoutNeedToRefetch', 'message': 'Przeczytano powiadomienie.'}
        notificationId = request.POST.get('id')
        notification = Notification.objects.get(pk=int(notificationId))
        notification.hasBeenSeen = True
        notification.save()
        return JsonResponse(responseData)


def eventTable(request):
    availableBookingDates = AvailableBookingDate.objects.filter(isDeleted=False)
    filteredAvailableBookingDates = []
    for availableBookingDate in availableBookingDates:
        if availableBookingDate.reservation_set.filter(isAccepted=True, isDeleted=False).count() == 0:
            filteredAvailableBookingDates.append(availableBookingDate)
    reservations = Reservation.objects.filter(isDeleted=False)

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


# class Event:
#     def __init__(self, eventId, eventType, startDate, endDate, serviceProvider=None, client=None):
#         self.eventId = eventId
#         self.eventType = eventType
#         self.startDate = startDate
#         self.endDate = endDate
#         self.serviceProvider = serviceProvider
#         self.client = client
#
#     def __str__(self):
#         if self.eventType == 0:
#             return f"Dostępny termin z id={self.eventId} od {self.startDate} do {self.endDate}. Usługodawca={self.serviceProvider.name} {self.serviceProvider.surname}"
#         elif self.eventType == 1:
#             return f"Propozycja rezerwacji z id={self.eventId} od {self.startDate} do {self.endDate}. Usługodawca={self.serviceProvider.name} {self.serviceProvider.surname}. Client={self.client.name} {self.client.surname}"
#         elif self.eventType == 2:
#             return f"Potwierdzona rezerwacja z id={self.eventId} od {self.startDate} do {self.endDate}. Usługodawca={self.serviceProvider.name} {self.serviceProvider.surname}. Client={self.client.name} {self.client.surname}"
#         elif self.eventType == 3:
#             return f"Propozycja terminu z id={self.eventId} od {self.startDate} do {self.endDate}. Client={self.client.name} {self.client.surname}"
#         else:
#             return f"Dziwne wydarzenie Id={self.eventId} od {self.startDate} do {self.endDate}."


# @login_required(login_url='login')
# def eventTable(request):
#     events = []
#     availableBookingDates = AvailableBookingDate.objects.filter(isDeleted=False)
#     for availableBookingDate in availableBookingDates:
#         event = Event(
#             eventId=availableBookingDate.id,
#             eventType=0,
#             startDate=availableBookingDate.start,
#             endDate=availableBookingDate.end,
#             serviceProvider=availableBookingDate.user)
#         events.append(event)
#     ic(events)
#     reservations = Reservation.objects.filter(isDeleted=False)
#     context = {'events': events}
#     return render(request, 'eventTable/eventTable.html', context)


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
            # messages.error(request, 'Username or password is incorrect')
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



# TESTY
def myTest(request):
    availableBookingDates = AvailableBookingDate.objects.filter(isDeleted=False)
    filteredAvailableBookingDates = []
    for availableBookingDate in availableBookingDates:
        if availableBookingDate.reservation_set.filter(isAccepted=True, isDeleted=False).count() == 0:
            filteredAvailableBookingDates.append(availableBookingDate)
    reservations = Reservation.objects.filter(isDeleted=False)
    context = {'availableBookingDates': filteredAvailableBookingDates,
               'reservations': reservations}
    return render(request, 'test/myTest.html', context)
# Wersja testowa THEME
from django.views.generic import ListView, DetailView

class PostListView(ListView):
    model = Post
    template_name = 'test/posts/main.html'

class PostDetailView(DetailView):
    model = Post
    template_name = 'test/posts/detail.html'
