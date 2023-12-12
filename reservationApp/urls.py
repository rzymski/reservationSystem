from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),

    path('register/', views.registerUser, name='register'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('userProfile/<pk>/', views.userProfile, name='userProfile'),
    path('updateUser', views.updateUser, name='updateUser'),

    path('restricted/', views.notForClients, name='notForClients'),

    path('allEvents/', views.allEvents, name='allEvents'),
    path('getEvents/<pk>/', views.getEvents, name='getEvents'),

    path('addAvailableBookingDateByCalendar/', views.addAvailableBookingDateByCalendar, name='addAvailableBookingDateByCalendar'),
    path('availableBookingDate/addAvailableBookingDate/', views.addAvailableBookingDate, name='addAvailableBookingDate'),
    path('availableBookingDate/editAvailableBookingDate/', views.editAvailableBookingDate, name='editAvailableBookingDate'),
    path('availableBookingDate/deleteAvailableBookingDate/', views.deleteAvailableBookingDate, name='deleteAvailableBookingDate'),


    path('test/main/', views.PostListView.as_view(), name='main'),
    path('test/<pk>/', views.PostDetailView.as_view(), name='detail'),
]
