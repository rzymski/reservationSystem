from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('test/main/', views.PostListView.as_view(), name='main'),
    path('test/<pk>/', views.PostDetailView.as_view(), name='detail'),
]
