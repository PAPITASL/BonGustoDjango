"""Modelos o aliases del modulo `productos`, aqui se maneja todo lo relacionado con productos y platos."""

# Se importan los modelos desde la capa de dominio
from bongusto.domain.models import Categoria, Menu, PedidoDetalle, Producto

# Aqui se definen los modelos que se usan en este modulo
__all__ = ["Producto", "Categoria", "Menu", "PedidoDetalle"]