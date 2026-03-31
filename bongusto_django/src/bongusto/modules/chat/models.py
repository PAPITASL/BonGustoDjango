"""
Modelos del módulo chat.

Este archivo solo sirve para traer (importar) el modelo que ya existe
y usarlo dentro del módulo chat.
"""

# Importamos el modelo de mensajes del chat
from bongusto.domain.models import MensajeChat


# Esto define qué se puede usar cuando se importa este archivo
# Es como decir: "solo quiero usar MensajeChat"
__all__ = ["MensajeChat"]