"""Modelos o aliases del modulo `pedidos`. Este archivo agrupa las entidades relacionadas con encabezados y detalles de pedidos."""


# ===== Importaciones | Dependencias necesarias para el funcionamiento del modulo `pedidos`. =====
from bongusto.domain.models import PedidoDetalle, PedidoEncabezado


# ===== Exportacion de modelos | Modulo `pedidos` | Define que entidades se exponen desde este archivo. =====
__all__ = ["PedidoEncabezado", "PedidoDetalle"]