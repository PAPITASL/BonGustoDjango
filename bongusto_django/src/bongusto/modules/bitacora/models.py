"""Modelos del módulo bitácora.
Aquí se trabajan las entidades relacionadas con el historial de acciones del sistema.
"""
# Se importan los modelos desde la capa de dominio.
# Este módulo no define modelos propios, solo usa los que ya existen.
# Así se mantiene todo más organizado a nivel de arquitectura.
from bongusto.domain.models import Bitacora, Usuario

# __all__ indica qué se puede importar desde este archivo.
# Si otro módulo usa import *, solo va a traer Bitacora y Usuario.
# Esto ayuda a tener control sobre lo que se expone.
__all__ = ["Bitacora", "Usuario"]