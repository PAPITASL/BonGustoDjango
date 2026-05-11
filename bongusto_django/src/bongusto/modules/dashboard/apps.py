"""Configuración del módulo `dashboard`: aquí se registra la app del panel principal y sus métricas."""

# Se importa AppConfig, que es la base que usa Django para registrar una app
from django.apps import AppConfig


# Clase que define cómo Django reconoce y maneja el módulo dashboard
class DashboardConfig(AppConfig):

    # Tipo de ID automático que usarán los modelos por defecto
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta completa donde está ubicado el módulo dentro del proyecto
    # Esto debe coincidir con la estructura real de carpetas
    name = "bongusto.modules.dashboard"

    # Nombre interno corto de la app
    # Sirve para identificarla dentro de Django sin chocar con otras
    label = "modules_dashboard"

    # Nombre más claro que puede mostrarse en el admin o en configuraciones
    verbose_name = "Modulo Dashboard"