"""Configuracion de la capa `interfaces`, responsable del enrutamiento y entrada HTTP principal."""

from django.apps import AppConfig


class InterfacesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bongusto.interfaces"
    label = "interfaces"
    verbose_name = "Interfaces BonGusto"
