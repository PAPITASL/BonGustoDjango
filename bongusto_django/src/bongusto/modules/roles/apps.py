"""Configuracion Django del modulo `roles`, aqui se maneja todo lo relacionado con los roles del sistema."""
# Se importa AppConfig que es lo que usa Django para registrar el modulo
from django.apps import AppConfig

# Clase principal del modulo roles
class RolesConfig(AppConfig):

    # Tipo de id automatico para los modelos
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del modulo dentro del proyecto
    name = "bongusto.modules.roles"

    # Nombre interno del modulo (para evitar conflictos)
    label = "modules_roles"

    # Nombre que se muestra en Django
    verbose_name = "Modulo Roles"