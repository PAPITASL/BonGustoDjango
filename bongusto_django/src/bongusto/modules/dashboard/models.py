"""Modelos o aliases del modulo `dashboard`. Este archivo identifica las entidades que pertenecen a resumen general y metricas del panel."""

# Importamos los modelos principales desde la capa domain
# (estos son los que realmente usa el dashboard para mostrar datos)
from bongusto.domain.models import Categoria, Menu, Musica, Producto, Reserva, Usuario

# __all__ sirve para definir que modelos se exportan cuando alguien hace:
# from modulo import *
# Es como decir: "estos son los modelos importantes de este modulo"
__all__ = [
    "Usuario",
    "Menu",
    "Producto",
    "Categoria",
    "Musica",
    "Reserva"
]
