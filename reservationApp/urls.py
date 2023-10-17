from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'przypadkowaNazwaWUrls'

urlpatterns = [
    path('', PostListView.as_view(), name='main'),
    path('<pk>/', PostDetailView.as_view(), name='detail'),
]
