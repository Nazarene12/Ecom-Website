from django.urls import re_path
from Ecom_Web import consumers

websocket_urlpatterns = [

    re_path(r'^ws/neworder/$', consumers.NotificationChannel.as_asgi()),
    re_path(r'ws/admin/$', consumers.AdminConsumer.as_asgi()),
]