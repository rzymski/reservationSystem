from django.shortcuts import render, redirect
from .models import *
from .forms import CreateUserForm, UpdateProfileForm, UpdateUserForm
from .decorators import unauthenticatedUser, allowedUsers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from icecream import ic
import json


def index(request):
    all_events = AvailableBookingDate.objects.all()

    clientsGroup = Group.objects.get(name='client')
    serviceProviders = User.objects.exclude(groups=clientsGroup)
    # serviceProviders = serviceProviderGroup.user_set.all()

    context = {
        "events": all_events,
        'serviceProviders': serviceProviders,
    }
    return render(request, 'calendar/calendar.html', context)


def allEvents(request):
    eventsObjects = AvailableBookingDate.objects.all()
    out = []
    for event in eventsObjects:
        out.append({
            'title': f"{event.user.first_name} {event.user.last_name}",
            'id': event.id,
            'start': event.start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': event.end.strftime('%Y-%m-%dT%H:%M:%S'),
            'color': '#378006',
            'serviceProviderId': event.user.id,
        })
    return JsonResponse(out, safe=False)


# def getEvents(request, pk):
#     ic("GET EVENTS WORK")
#     eventsObjects = AvailableBookingDate.objects.filter(user=pk)
#     out = []
#     for event in eventsObjects:
#         out.append({
#             'title': f"{event.user.first_name} {event.user.last_name}",
#             'id': event.id,
#             'start': event.start.strftime('%Y-%m-%dT%H:%M:%S'),
#             'end': event.end.strftime('%Y-%m-%dT%H:%M:%S')
#         })
#     return JsonResponse(out, safe=False)


def filterServiceProviders(request):
    if request.method == 'POST':
        selectedOptionsJson = request.POST.get('selected_options')
        selectedOptions = json.loads(selectedOptionsJson)
        selectedIds = [option['id'] for option in selectedOptions]
        if len(selectedIds) == 0:
            return redirect('allEvents')
        ic(selectedIds)
        eventsObjects = AvailableBookingDate.objects.filter(user__id__in=selectedIds)
        ic(eventsObjects)
        out = []
        for event in eventsObjects:
            out.append({
                'title': f"{event.user.first_name} {event.user.last_name}",
                'id': event.id,
                'start': event.start.strftime('%Y-%m-%dT%H:%M:%S'),
                'end': event.end.strftime('%Y-%m-%dT%H:%M:%S'),
                'color': '#378006',
                'serviceProviderId': event.user.id,
            })
        return JsonResponse(out, safe=False)
    ic("NIGDY NIE POWINNO SIE ZDARZYC")
    return redirect('allEvents')


@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def addAvailableBookingDateByCalendar(request):
    ic("Dodano event")
    if request.method == 'POST':
        ic(request.POST)
        # title = request.POST.get('title')
        startTimeSTR = request.POST.get('startTime')
        endTimeSTR = request.POST.get('endTime')
        startDateSTR = request.POST.get('startStr')
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
        start = datetime.combine(startDate, startTime)
        end = datetime.combine(startDate, endTime)
        currentUser = request.user
        availableBookingDate = AvailableBookingDate(user=currentUser, start=start, end=end)
        availableBookingDate.save()

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
        startTime = datetime.strptime(startTimeSTR, '%H:%M').time()
        endTime = datetime.strptime(endTimeSTR, '%H:%M').time()
        startDate = datetime.strptime(startDateSTR, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDateSTR, '%Y-%m-%d').date()
        start = datetime.combine(startDate, startTime)
        end = datetime.combine(endDate, endTime)
        currentUser = request.user
        availableBookingDate = AvailableBookingDate(user=currentUser, start=start, end=end)
        availableBookingDate.save()
    ic("DZIALA")
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
        availableBookingDate.save()
    ic("DZIALA")
    return redirect('index')

@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def deleteAvailableBookingDate(request):
    ic("Usunieto dostepny termin")
    if request.method == 'POST':
        id = request.POST.get('selectedEvent')
        availableBookingDate = AvailableBookingDate.objects.get(pk=id)
        availableBookingDate.delete()
    return redirect('index')

@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def notForClients(request):
    return render(request, 'calendar/restricted.html')


@login_required(login_url='login')
def userProfile(request, pk):
    userOwnerOfProfile = User.objects.get(pk=pk)
    userProfileInstance = UserProfile.objects.get(user=userOwnerOfProfile)
    return render(request, 'accounts/userProfile.html', {"userProfile": userProfileInstance})



@login_required
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
            # messages.success(request, 'Account was createf for ' + username)
            # return redirect('login')
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    return render(request, 'accounts/register.html', {'form': form})


@unauthenticatedUser
def loginUser(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST['next'])
            return redirect('index')
        else:
            messages.info(request, 'Username or password is incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)


def logoutUser(request):
    theme = True if 'is_dark_theme' in request.session else False
    logout(request)
    if theme:
        request.session["is_dark_theme"] = True
    return redirect('index')




# Wersja testowa THEME
from django.views.generic import ListView, DetailView

class PostListView(ListView):
    model = Post
    template_name = 'test/posts/main.html'

class PostDetailView(DetailView):
    model = Post
    template_name = 'test/posts/detail.html'
