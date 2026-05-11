"""Modelos o aliases del modulo `roles`, aqui se maneja lo relacionado con roles y permisos."""

# Se importan los modelos desde la capa de dominio
from bongusto.domain.models import Permiso, Rol

# Aqui se definen los modelos que se usan en este modulo
__all__ = ["Rol", "Permiso"]