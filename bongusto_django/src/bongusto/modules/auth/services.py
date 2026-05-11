"""Servicios del módulo auth.

Aquí es donde se maneja la lógica de la autenticación.
O sea, no son vistas ni modelos, sino lo que realmente hace funcionar el login y todo eso.
"""

# Se importa el servicio de Usuario desde la capa de aplicación.
# Aquí es donde está la lógica real (login, validaciones, etc).
# No viene de models sino de services, que es la forma correcta de organizarlo.
from bongusto.application.services import UsuarioService


# __all__ define qué se puede importar desde este archivo.
# En este caso solo dejamos disponible UsuarioService para otros módulos.
__all__ = ["UsuarioService"]