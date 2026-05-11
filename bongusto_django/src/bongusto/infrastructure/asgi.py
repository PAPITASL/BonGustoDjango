"""
infrastructure/asgi.py
Este es el punto de entrada del proyecto cuando se usa ASGI.
Aquí se define cómo Django maneja tanto HTTP como WebSockets (chat en tiempo real).
"""

import os
import django

# Aquí se define cuál archivo de configuración usar
# (básicamente le decimos a Django dónde están los settings del proyecto)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bongusto.infrastructure.settings")

# Inicializa Django
# Sin esto el proyecto no carga correctamente
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from bongusto.infrastructure import routing

# Esta es la app principal ASGI
# Aquí se separa el tráfico según el tipo de conexión
application = ProtocolTypeRouter(
    {
        # Peticiones normales (views, templates, etc.)
        # Todo lo clásico de Django entra por HTTP
        "http": get_asgi_application(),

        # Conexiones en tiempo real (chat, sockets, etc.)
        "websocket": AuthMiddlewareStack(
            # Permite manejar sesiones y autenticación en WebSockets
            URLRouter(routing.websocket_urlpatterns)
            # Aquí se usan las rutas definidas en routing.py para WebSockets
        ),
    }
)