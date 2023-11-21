from django.shortcuts import render, redirect
from .models import Post, Events
from .forms import CreateUserForm
from .decorators import unauthenticatedUser, allowedUsers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.http import JsonResponse
from icecream import ic

def index(request):
    ic("INDEX")
    all_events = Events.objects.all()
    context = {
        "events": all_events,
    }
    return render(request, 'calendar/calendar.html', context)

def allEvents(request):
    eventsObjects = Events.objects.all()
    out = []
    for event in eventsObjects:
        print(event)
        out.append({
            'title': event.name,
            'id': event.id,
            'start': event.start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': event.end.strftime('%Y-%m-%dT%H:%M:%S')
        })
    return JsonResponse(out, safe=False)

def addEvent(request):
    ic("Dodano event")
    ic(request)
    if request.method == 'POST':
        title = request.POST.get('title')
        startTime = request.POST.get('startTime')
        endTime = request.POST.get('endTime')
        startStr = request.POST.get('startStr')
        # event = Events(name=str(title), start=startTime, end=endTime)
        # event.save()
        ic(title, startTime, endTime, startStr)
    ic("NADAL DZIALA")
    return index(request)

# def addEvent(request):
#     print("Dodano event")
#     start = request.GET.get("start", None)
#     end = request.GET.get("end", None)
#     title = request.GET.get("title", None)
#     event = Events(name=str(title), start=start, end=end)
#     event.save()
#     data = {}
#     return JsonResponse(data)

def addEventJSON(request):
    if request.method == 'GET':
        ic("Dodano event")
        start = request.GET.get("start", None)
        end = request.GET.get("end", None)
        title = request.GET.get("title", None)
        ic(start, end, title)
        event = Events(name=str(title), start=start, end=end)
        event.save()
        data = {'success': True}
        return JsonResponse(data)
    else:
        data = {'success': False}
        return JsonResponse(data)


@allowedUsers(allowedGroups=['admin', 'controller', 'serviceProvider'])
def notForClients(request):
    return render(request, 'calendar/restricted.html')

@login_required(login_url='login')
def userProfile(request):
    return render(request, 'accounts/userProfile.html')


@unauthenticatedUser
def registerUser(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            clientGroup = Group.objects.get(name='client')
            user.groups.add(clientGroup)
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was createf for ' + username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


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
