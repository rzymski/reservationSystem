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
    serviceProviders = User.objects.filter(availablebookingdate__isnull=False, availablebookingdate__isDeleted=False).distinct()
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
    reservations = Reservation.objects.filter(availableBookingDate__isnull=True, isDeleted=False)
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
    reservations = Reservation.objects.filter(isAccepted=False, availableBookingDate__isnull=False, availableBookingDate__isDeleted=False, isDeleted=False) if allServiceProviders else Reservation.objects.filter(isAccepted=False, availableBookingDate__isnull=False, availableBookingDate__isDeleted=False, isDeleted=False, availableBookingDate__user__id__in=selectedIds)
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
    reservations = Reservation.objects.filter(isAccepted=True, isDeleted=False) if allServiceProviders else Reservation.objects.filter(isAccepted=True, isDeleted=False, availableBookingDate__user__id__in=selectedIds)
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
    availableBookingDates = AvailableBookingDate.objects.filter(isDeleted=False) if allServiceProviders else AvailableBookingDate.objects.filter(isDeleted=False, user__id__in=selectedIds)
    out = []
    for availableBookingDate in availableBookingDates:
        freeTimesInAvailableBookingDate = getAvailableTimeRanges(availableBookingDate)
        for freeTime in freeTimesInAvailableBookingDate:
            possibleDragging = True if Reservation.objects.filter(isAccepted=True, availableBookingDate=availableBookingDate, isDeleted=False).count() == 0 else False
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
        # allReservationsWithoutServiceProviderJSON = allReservationsWithoutServiceProvider(request, allServiceProviders=False, selectedIds=selectedIds)
        combinedResponse = {
            'availableDates': json.loads(allAvailableBookingDatesJSON.content),
            'unconfirmedReservations': json.loads(allUnconfirmedReservationsJSON.content),
            'confirmedReservations': json.loads(allConfirmedReservationsJSON.content),
            # 'reservationsWithoutServiceProvider': json.loads(allReservationsWithoutServiceProviderJSON.content),
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
                    Notification.createNotification(7, availableBookingDate.user, currentUser, availableBookingDate, None)
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
                Notification.createNotification(2, reservation.availableBookingDate.user, currentUser, reservation.availableBookingDate, reservation)
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
                        Notification.createNotification(8, reservation.bookingPerson, currentUser, None, reservation)
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
                Notification.createNotification(6, availableBookingDate.user, currentUser, availableBookingDate, None)
        else:
            reservation = Reservation.objects.get(pk=int(eventId))
            reservation.isDeleted = True
            reservation.save()
            ic("Usunieto rezerwacje")
            if currentUser != reservation.bookingPerson:
                if int(eventTypeId) == 1:
                    print(f"{currentUser} usunal rezerwacje uzytkownika {reservation.bookingPerson}")
                    Notification.createNotification(4, reservation.bookingPerson, currentUser, None, reservation)
                elif int(eventTypeId) == 2:
                    print(f"{currentUser} usunal potwierdzony termin dotyczacy {reservation.bookingPerson} i {reservation.availableBookingDate.user}")
                    Notification.createNotification(3, reservation.bookingPerson, currentUser, None, reservation)
                elif int(eventTypeId) == 3:
                    print(f"{currentUser} usunal propozycje terminu uzytkownika {reservation.bookingPerson}")
                    Notification.createNotification(5, reservation.bookingPerson, currentUser, None, reservation)
                else:
                    raise Exception(f"To nie powinno sie wydarzyc. eventType = {eventTypeId}")
            elif int(eventTypeId) == 2 and reservation.availableBookingDate.user != currentUser:
                print(f"{currentUser} usunal potwierdzony termin dotyczacy {reservation.bookingPerson} i {reservation.availableBookingDate.user}")
                Notification.createNotification(3, reservation.bookingPerson, currentUser, reservation.availableBookingDate, None)
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
                Notification.createNotification(1, reservation.bookingPerson, userWhoConfirmedReservation, None, reservation)
            elif action == 'confirmExist':
                errorMessage = saveReservationWhichCouldBePartOfAvailableBookingData(reservation, userWhoConfirmedReservation)
                if errorMessage:
                    messages.error(request, errorMessage)
            elif action == 'reject':
                reservation.isDeleted = True
                reservation.save()
                Notification.createNotification(4, reservation.bookingPerson, userWhoConfirmedReservation, None, reservation)
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
                    Notification.createNotification(7, availableBookingDate.user, currentUser, availableBookingDate, None)
            if eventType == 3 or eventType == 1:
                reservation = Reservation.objects.get(id=eventId)
                reservation.start = newStartDate
                reservation.end = newEndDate
                reservation.save()
                if currentUser != reservation.bookingPerson and eventType == 3:
                    print(f"{currentUser} edytował propozycje terminu uzytkownika {reservation.bookingPerson}")
                    Notification.createNotification(8, reservation.bookingPerson, currentUser, None, reservation)
        except ValidationError as e:
            ic("JEST ERROR?", e)
            responseData = {'status': 'error', 'message': e.message}
        return JsonResponse(responseData)


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
