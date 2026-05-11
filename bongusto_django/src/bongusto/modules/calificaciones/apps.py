"""
Configuración del módulo calificaciones.
Aquí se define cómo Django reconoce esta app dentro del proyecto.
Este módulo es el que maneja las opiniones y puntajes de los clientes.
"""
# Se importa AppConfig, que es la base para registrar una app en Django
from django.apps import AppConfig

# Clase de configuración del módulo calificaciones
class CalificacionesConfig(AppConfig):

    # Tipo de id automático que usarán los modelos (BigAutoField)
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta completa donde está el módulo dentro del proyecto
    # Django usa esto para ubicar correctamente la app
    name = "bongusto.modules.calificaciones"

    # Nombre interno corto de la app
    # Sirve para identificarla sin chocar con otras apps
    label = "modules_calificaciones"

    # Nombre más legible que se puede mostrar en el admin u otras partes
    verbose_name = "Modulo Calificaciones"