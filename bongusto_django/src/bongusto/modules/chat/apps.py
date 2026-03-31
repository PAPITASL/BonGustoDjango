"""
Configuración del módulo chat.

Aquí se registra la app que maneja el chat interno y el soporte en tiempo real.
"""

# Importamos AppConfig
# Esto sirve para registrar el módulo en Django
from django.apps import AppConfig


# Configuración del módulo chat
class ChatConfig(AppConfig):

    # Tipo de ID automático que usarán los modelos
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta real del módulo dentro del proyecto
    name = "bongusto.modules.chat"

    # Nombre interno del módulo
    label = "modules_chat"

    # Nombre más visual o más entendible
    verbose_name = "Modulo Chat"