from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'systemOfReservationsApp'

urlpatterns = [
    path('', views.index, name='index'),
    path('main/', views.PostListView.as_view(), name='main'),
    path('<pk>/', views.PostDetailView.as_view(), name='detail'),
]
