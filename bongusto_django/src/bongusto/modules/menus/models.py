"""Modelos del modulo menus, aqui se usan las entidades principales relacionadas con los menus del sistema."""

# Importamos los modelos necesarios desde la capa domain
# Estos son los que realmente se usan en este modulo
from bongusto.domain.models import Menu, PedidoDetalle, Producto


# Definimos que se puede usar cuando alguien importa este modulo
# Es como decir: estos son los modelos importantes aqui
__all__ = [
    "Menu",
    "Producto",
    "PedidoDetalle",
]