"""Configuracion del modulo de notificaciones."""

from django.apps import AppConfig


class NotificacionesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bongusto.modules.notificaciones"
    label = "modules_notificaciones"
    verbose_name = "Modulo Notificaciones"

