"""Configuracion del modulo mesas."""

from django.apps import AppConfig


class MesasConfig(AppConfig):
    """Registra el modulo de mesas dentro del proyecto Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "bongusto.modules.mesas"
    label = "modules_mesas"
    verbose_name = "Modulo Mesas"

