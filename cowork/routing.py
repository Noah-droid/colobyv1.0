from django.urls import path, re_path

from cowork import consumers

websocket_urlpatterns = [
    path('chat/<str:room_slug>/', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chat/send/(?P<room_slug>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chat/get/(?P<room_slug>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
