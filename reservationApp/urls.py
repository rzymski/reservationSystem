from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.calendar, name='calendar'),

    path('register/', views.registerUser, name='register'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('userProfile/<pk>/', views.userProfile, name='userProfile'),
    path('updateUser', views.updateUser, name='updateUser'),

    path('allAvailableBookingDates/', views.allAvailableBookingDates, name='allAvailableBookingDates'),
    path('allUnconfirmedReservations/', views.allUnconfirmedReservations, name='allUnconfirmedReservations'),
    path('allConfirmedReservations/', views.allConfirmedReservations, name='allConfirmedReservations'),
    path('allReservationsWithoutServiceProvider/', views.allReservationsWithoutServiceProvider, name='allReservationsWithoutServiceProvider'),

    path('filterServiceProviders/', views.filterServiceProviders, name='filterServiceProviders'),

    path('addEditAvailableBookingDate/', views.addEditAvailableBookingDate, name='addEditAvailableBookingDate'),
    path('deleteEvent/', views.deleteEvent, name='deleteEvent'),
    path('addEditReservation/', views.addEditReservation, name='addEditReservation'),
    path('confirmOrRejectReservation/', views.confirmOrRejectReservation, name='confirmOrRejectReservation'),
    path('dragEvent/', views.dragEvent, name='dragEvent'),

    path('deleteNotification/', views.deleteNotification, name='deleteNotification'),
    path('readNotification/', views.readNotification, name='readNotification'),

    path('eventTable/', views.eventTable, name='eventTable'),

    path('createStatistics/', views.createStatistics, name='createStatistics'),


    path('test/main/', views.PostListView.as_view(), name='main'),
    path('test/<pk>/', views.PostDetailView.as_view(), name='detail'),
    path('test/myTest', views.myTest, name='myTest')
]
