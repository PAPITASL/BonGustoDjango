"""
Modelos del módulo chat.

Este archivo básicamente solo reutiliza el modelo que ya existe
para poder usarlo dentro de este módulo.
"""

# Se importa el modelo de mensajes del chat desde la capa de dominio
from bongusto.domain.models import MensajeChat


# __all__ define qué se puede importar desde este archivo
# En este caso solo se expone MensajeChat
__all__ = ["MensajeChat"]