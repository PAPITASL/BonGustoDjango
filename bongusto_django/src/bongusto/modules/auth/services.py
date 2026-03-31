"""Servicios del módulo auth.
Aquí se agrupa la lógica de negocio relacionada con autenticación.
"""

# Importamos el servicio que maneja la lógica de Usuario
# Este servicio viene de la capa de aplicación (no de modelos)
from bongusto.application.services import UsuarioService


# __all__ define qué se puede importar desde este archivo
# Solo estamos exponiendo UsuarioService
__all__ = ["UsuarioService"]