from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [

    path('counter/', views.counter, name='counter'),
    # path('index/', views.Index.as_view(), name='Index'),
    # path('<str:room_name>', views.Rooom.as_view(), name='room'),

    path('', views.index, name='index'),

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

    path('changeNotificationStatus/', views.changeNotificationStatus, name='changeNotificationStatus'),


    path('test/main/', views.PostListView.as_view(), name='main'),
    path('test/<pk>/', views.PostDetailView.as_view(), name='detail'),
    path('test/myTest', views.myTest, name='myTest')
]
