"""Modelos o aliases del modulo `perfil`, aqui se maneja lo relacionado con el usuario."""

# Se importa el modelo Usuario desde la capa de dominio
from bongusto.domain.models import Usuario

# Aqui se define que modelo se usa en este modulo
__all__ = ["Usuario"]