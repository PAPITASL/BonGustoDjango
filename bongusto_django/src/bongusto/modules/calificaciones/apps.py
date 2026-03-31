"""
Configuración del módulo calificaciones.

Aquí se registra la app que maneja opiniones y puntajes de clientes.
"""

# Importamos AppConfig (esto es lo que usa Django para registrar apps)
from django.apps import AppConfig


# Configuración del módulo calificaciones
class CalificacionesConfig(AppConfig):

    # Tipo de id automático (llave primaria en modelos)
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del módulo dentro del proyecto
    name = "bongusto.modules.calificaciones"

    # Nombre interno (sirve para evitar conflictos entre apps)
    label = "modules_calificaciones"

    # Nombre bonito (se usa en admin o configuraciones)
    verbose_name = "Modulo Calificaciones"
