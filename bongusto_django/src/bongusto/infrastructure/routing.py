"""Rutas WebSocket del proyecto."""

from django.urls import re_path

from bongusto.modules.chat.consumers import ChatConsumer
from bongusto.modules.musica.consumers import MusicaQueueConsumer
from bongusto.modules.shared.consumers import OperacionMesasConsumer


websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<participante>[\w\-]+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/operacion/mesas/$", OperacionMesasConsumer.as_asgi()),
    re_path(r"ws/musica/cola/$", MusicaQueueConsumer.as_asgi()),
]
