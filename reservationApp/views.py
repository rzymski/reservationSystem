from django.shortcuts import render
from .models import *

from django.views.generic import ListView, DetailView



def index(request):
    print("OK")
    return render(request, 'calendar/calendar.html')


class PostListView(ListView):
    model = Post
    template_name = 'posts/main.html'

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'
