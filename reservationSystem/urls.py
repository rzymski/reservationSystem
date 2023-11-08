from django.contrib import admin
from django.urls import path, include
from theme.views import change_theme

urlpatterns = [
    path('admin/', admin.site.urls),
    path('switch-theme/', change_theme, name="change-theme"), #switch_theme url musi być powyżej reservationApp.urls
    path('', include('reservationApp.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
]
