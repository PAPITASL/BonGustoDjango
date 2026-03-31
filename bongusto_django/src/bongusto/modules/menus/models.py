"""Modelos del modulo menus, aqui se agrupan las entidades relacionadas con la gestion de menus del sistema."""

# ===== Importaciones principales | Se traen los modelos desde la capa de dominio. =====
from bongusto.domain.models import Menu, PedidoDetalle, Producto


# ===== Exportacion de modelos | Se define que modelos quedan disponibles en este modulo. =====
__all__ = [
    "Menu",
    "Producto",
    "PedidoDetalle",
]