"""Configuracion de la app `domain`.
Aqui viven los modelos principales del sistema (las tablas ORM de Django).
Es como el núcleo de datos de todo BonGusto.
"""

from django.apps import AppConfig


class DomainConfig(AppConfig):
    # Define el tipo de ID automático por defecto
    # BigAutoField es mejor cuando el sistema crece mucho
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del módulo dentro del proyecto
    # Django usa esto para saber dónde está esta app
    name = "bongusto.domain"

    # Nombre interno corto
    # Sirve para identificar la app sin conflictos
    label = "domain"

    # Nombre más amigable
    # Este es el que se muestra en el admin o configuraciones
    verbose_name = "Dominio BonGusto"
