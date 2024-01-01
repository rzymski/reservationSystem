from django.urls import path
from .consumers import TestConsumer

from django.urls import re_path

websocket_urlpatterns = [
    path("ws/test/", TestConsumer.as_asgi())
    #path('ws/receive/', ReceiveNotification.as_asgi()),
    #re_path(r'ws/receive/$', ReceiveNotification.as_asgi()),
]
