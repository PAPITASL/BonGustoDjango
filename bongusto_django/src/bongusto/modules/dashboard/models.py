"""Modelos o aliases del modulo `dashboard`. Aquí se agrupan las entidades que usa el panel para mostrar la información general."""

# Se importan los modelos desde la capa de dominio
# Estos son los que el dashboard necesita para mostrar datos reales del sistema
from bongusto.domain.models import Categoria, Menu, Musica, Producto, Reserva, Usuario

# __all__ define qué modelos se pueden usar cuando otro archivo importa este módulo
# Básicamente indica cuáles son los más importantes dentro del dashboard
__all__ = [
    "Usuario",
    "Menu",
    "Producto",
    "Categoria",
    "Musica",
    "Reserva"
]