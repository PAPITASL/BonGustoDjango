"""Modelos o aliases del modulo `pedidos`, aqui se agrupa todo lo de encabezados y detalles de pedidos."""


# Se importan los modelos desde la capa de dominio
from bongusto.domain.models import PedidoDetalle, PedidoEncabezado, SolicitudPago


# Aqui se define que modelos se van a usar en este modulo
__all__ = ["PedidoEncabezado", "PedidoDetalle", "SolicitudPago"]
