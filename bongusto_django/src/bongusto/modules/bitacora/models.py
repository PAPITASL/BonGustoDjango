"""Modelos del módulo bitácora.
Aquí se exponen las entidades relacionadas con el historial de acciones.
"""

# Importamos los modelos desde la capa de dominio
# O sea, los modelos reales no están aquí, sino en otra parte del proyecto
from bongusto.domain.models import Bitacora, Usuario


# __all__ define qué se puede importar desde este archivo
# En este caso estamos exponiendo Bitacora y Usuario
__all__ = ["Bitacora", "Usuario"]

