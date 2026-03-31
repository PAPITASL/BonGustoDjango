"""Modelos o aliases del modulo `usuarios`. Este archivo define las entidades relacionadas con usuarios del sistema y clientes API."""


# ===== Importaciones | Modelos del dominio que este modulo utiliza o expone. =====
from bongusto.domain.models import Bitacora, PedidoEncabezado, Reserva, Rol, Usuario


# ===== Exportaciones | Define que modelos se exponen cuando se importa este modulo. =====
__all__ = [
    "Usuario",           # Entidad principal del sistema (usuarios y clientes)
    "Rol",               # Define permisos y tipos de usuario
    "PedidoEncabezado",  # Relacion de pedidos realizados por el usuario
    "Reserva",           # Reservas hechas por el usuario
    "Bitacora",          # Historial de acciones del usuario en el sistema
]