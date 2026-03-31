"""Modelos o aliases del modulo `productos`. Representa las entidades relacionadas con platos y productos del restaurante."""

# ===== Importaciones | Dependencias que este archivo necesita para funcionar dentro del modulo. =====
from bongusto.domain.models import Categoria, Menu, PedidoDetalle, Producto



# ===== Exportaciones | Modulo `productos` | Define los modelos disponibles para uso en otras capas. =====
__all__ = ["Producto", "Categoria", "Menu", "PedidoDetalle"]