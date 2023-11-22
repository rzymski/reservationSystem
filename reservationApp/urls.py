from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),

    path('register/', views.registerUser, name='register'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('userProfile/', views.userProfile, name='userProfile'),

    path('restricted/', views.notForClients, name='notForClients'),

    path('allEvents/', views.allEvents, name='allEvents'),
    path('addEvent/', views.addEvent, name='addEvent'),

    path('availableBookingDate/addAvailableBookingDate/', views.addAvailableBookingDate, name='addAvailableBookingDate'),
    path('availableBookingDate/deleteAvailableBookingDate/', views.deleteAvailableBookingDate, name='deleteAvailableBookingDate'),


    path('test/main/', views.PostListView.as_view(), name='main'),
    path('test/<pk>/', views.PostDetailView.as_view(), name='detail'),
]
