from django.shortcuts import render
from .models import *

from django.views.generic import ListView, DetailView



def index(request):
    print("OK")
    return render(request, 'calendar/calendar.html')













# Wersja testowa THEME
class PostListView(ListView):
    model = Post
    template_name = 'test/posts/main.html'

class PostDetailView(DetailView):
    model = Post
    template_name = 'test/posts/detail.html'
