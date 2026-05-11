"""Modelos del módulo auth.

Aquí básicamente se manejan los modelos que necesita la parte de autenticación.
En este caso solo se usa el modelo Usuario.
"""

# Se importa el modelo Usuario desde domain.
# Este módulo no lo crea, solo lo reutiliza para mantener todo organizado.
from bongusto.domain.models import Usuario


# __all__ sirve para definir qué se puede importar desde este archivo.
# O sea, si otro módulo hace un import *, solo va a traer Usuario.
# Esto ayuda a que todo sea más claro y controlado.
__all__ = ["Usuario"]