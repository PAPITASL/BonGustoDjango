"""Configuración de la capa `interfaces`.
Esta capa es la que conecta todo lo que el usuario ve (URLs) con la lógica del sistema (vistas).
"""

from django.apps import AppConfig

class InterfacesConfig(AppConfig):
    
    # Tipo de ID automático por defecto.
    # Esto hace que las tablas usen BigAutoField (mejor para crecer en datos).
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del módulo dentro del proyecto.
    # Django usa esto para saber dónde está esta app.
    name = "bongusto.interfaces"

    # Nombre interno de la app.
    # Sirve para identificarla dentro del sistema sin conflictos.
    label = "interfaces"

    # Nombre más amigable.
    # Es el que se puede mostrar en admin o configuraciones.
    verbose_name = "Interfaces BonGusto"