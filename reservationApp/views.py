from django.shortcuts import render
from .models import *

from django.views.generic import ListView, DetailView

class PostListView(ListView):
    model = Post
    template_name = 'posts/main.html'

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'
