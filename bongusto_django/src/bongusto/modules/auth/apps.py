"""Configuración Django del módulo auth.
Aquí se define la configuración básica del módulo de autenticación.
"""

# Importamos AppConfig, que sirve para registrar y configurar una app en Django
from django.apps import AppConfig


# Esta clase representa la configuración del módulo auth dentro del proyecto
class AuthConfig(AppConfig):
    # Define el tipo de llave primaria automática que Django usará por defecto
    default_auto_field = "django.db.models.BigAutoField"

    # Nombre completo de la app dentro del proyecto
    name = "bongusto.modules.auth"

    # Nombre interno corto para identificar esta app en Django
    label = "modules_auth"

    # Nombre más amigable que puede mostrarse en paneles o configuraciones
    verbose_name = "Modulo Auth"