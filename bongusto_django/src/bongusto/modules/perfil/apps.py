"""Configuracion Django del modulo `perfil`, aqui se maneja todo lo del perfil del usuario."""
# Se importa AppConfig que es lo que usa Django para registrar el modulo
from django.apps import AppConfig
# Clase principal del modulo perfil
class PerfilConfig(AppConfig):
    # Tipo de id automatico para los modelos
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del modulo dentro del proyecto
    name = "bongusto.modules.perfil"

    # Nombre interno del modulo
    label = "modules_perfil"

    # Nombre que se muestra en Django
    verbose_name = "Modulo Perfil"
