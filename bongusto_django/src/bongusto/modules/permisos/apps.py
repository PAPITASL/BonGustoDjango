"""Configuracion Django del modulo `permisos`, aqui se maneja todo lo de permisos del sistema."""

# Se importa AppConfig que es lo que usa Django para registrar el modulo
from django.apps import AppConfig

# Clase principal del modulo permisos
class PermisosConfig(AppConfig):
    # Tipo de id automatico para los modelos
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del modulo dentro del proyecto
    name = "bongusto.modules.permisos"

    # Nombre interno del modulo
    label = "modules_permisos"

    # Nombre que se muestra en Django
    verbose_name = "Modulo Permisos"