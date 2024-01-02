from django.contrib import admin
from django.urls import path, include, re_path
from theme.views import change_theme
from django.conf import settings
from django.conf.urls.static import static

from  django.views.static import serve
urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('admin/', admin.site.urls),
    path('switch-theme/', change_theme, name="change-theme"), #switch_theme url musi być powyżej reservationApp.urls
    path('', include('reservationApp.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
