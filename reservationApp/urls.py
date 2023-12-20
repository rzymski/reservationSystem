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

    path('allAvailableBookingDates/', views.allAvailableBookingDates, name='allAvailableBookingDates'),
    path('filterServiceProviders/', views.filterServiceProviders, name='filterServiceProviders'),

    path('addAvailableBookingDateByCalendar/', views.addAvailableBookingDateByCalendar, name='addAvailableBookingDateByCalendar'),
    path('addAvailableBookingDate/', views.addAvailableBookingDate, name='addAvailableBookingDate'),
    path('editAvailableBookingDate/', views.editAvailableBookingDate, name='editAvailableBookingDate'),
    path('deleteAvailableBookingDate/', views.deleteAvailableBookingDate, name='deleteAvailableBookingDate'),

    path('allUnconfirmedReservations/', views.allUnconfirmedReservations, name='allUnconfirmedReservations'),
    path('allConfirmedReservations/', views.allConfirmedReservations, name='allConfirmedReservations'),

    path('reserveEntireBookingDate/', views.reserveEntireBookingDate, name='reserveEntireBookingDate'),
    path('reservePartSingleDayBookingDate/', views.reservePartSingleDayBookingDate, name='reservePartSingleDayBookingDate'),
    path('reservePartMultipleDaysBookingDate/', views.reservePartMultipleDaysBookingDate, name='reservePartMultipleDaysBookingDate'),
    path('deleteReservation/', views.deleteReservation, name='deleteReservation'),
    path('confirmOrRejectReservation/', views.confirmOrRejectReservation, name='confirmOrRejectReservation'),
    path('reserveIntervalOfBookingDate/', views.reserveIntervalOfBookingDate, name='reserveIntervalOfBookingDate'),

    path('dragEvent/', views.dragEvent, name='dragEvent'),

    path('allReservationsWithoutServiceProvider/', views.allReservationsWithoutServiceProvider, name='allReservationsWithoutServiceProvider'),
    path('addDesiredReservationDateByCalendar/', views.addDesiredReservationDateByCalendar, name="addDesiredReservationDateByCalendar"),
    path('confirmDesiredReservationProposition/', views.confirmDesiredReservationProposition, name="confirmDesiredReservationProposition"),
    path('editDesiredReservationDate/', views.editDesiredReservationDate, name='editDesiredReservationDate'),
    path('deleteDesiredReservationDate/', views.deleteDesiredReservationDate, name='deleteDesiredReservationDate'),
    path('addDesiredReservationDate/', views.addDesiredReservationDate, name='addDesiredReservationDate'),

    path('test/main/', views.PostListView.as_view(), name='main'),
    path('test/<pk>/', views.PostDetailView.as_view(), name='detail'),
    path('test/myTest', views.myTest, name='myTest')
]
