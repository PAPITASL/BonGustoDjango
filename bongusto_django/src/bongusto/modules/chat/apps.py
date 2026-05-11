"""
Configuración del módulo chat.
Aquí se define cómo Django reconoce esta app dentro del proyecto.
Este módulo es el encargado del chat interno y la comunicación en tiempo real.
"""
# Se importa AppConfig, que es la base para registrar una app en Django
from django.apps import AppConfig
# Clase de configuración del módulo chat
class ChatConfig(AppConfig):
    # Tipo de ID automático que usarán los modelos (BigAutoField)
    default_auto_field = "django.db.models.BigAutoField"
    # Ruta completa del módulo dentro del proyecto
    # Django usa esto para ubicar correctamente la app
    name = "bongusto.modules.chat"
    # Nombre interno corto de la app
    # Sirve para identificarla sin chocar con otras apps
    label = "modules_chat"
    # Nombre más claro que puede mostrarse en el admin u otras partes
    verbose_name = "Modulo Chat"