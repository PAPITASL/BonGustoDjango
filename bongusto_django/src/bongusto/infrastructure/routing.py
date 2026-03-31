"""
infrastructure/routing.py
Rutas WebSocket para el chat en tiempo real.
"""

from django.urls import re_path

from bongusto.modules.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<participante>[\w\-]+)/$", ChatConsumer.as_asgi()),
]
