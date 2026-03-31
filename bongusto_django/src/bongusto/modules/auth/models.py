"""Modelos del módulo auth.
Aquí se exponen las entidades que usa autenticación (por ejemplo Usuario).
"""

# Importamos el modelo Usuario desde la capa de dominio
# O sea, este modelo no está aquí directamente, sino en otra parte del proyecto
from bongusto.domain.models import Usuario


# __all__ define qué se puede importar cuando otro archivo hace:
# from ... import *
# En este caso solo estamos exponiendo Usuario
__all__ = ["Usuario"]
