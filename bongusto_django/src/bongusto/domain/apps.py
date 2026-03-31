"""Configuracion de la app `domain`, donde viven los modelos ORM centrales del proyecto."""

from django.apps import AppConfig


class DomainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bongusto.domain"
    label = "domain"
    verbose_name = "Dominio BonGusto"
