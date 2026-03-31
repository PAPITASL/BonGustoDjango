"""
infrastructure/asgi.py
Punto de entrada ASGI: HTTP + WebSocket (chat en tiempo real).
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bongusto.infrastructure.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from bongusto.infrastructure import routing

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns)),
    }
)
