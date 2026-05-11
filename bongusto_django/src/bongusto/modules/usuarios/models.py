"""Modelos o aliases del modulo `usuarios`.
Este archivo funciona como un punto central donde se agrupan
y se exponen las entidades relacionadas con usuarios del sistema
y clientes que interactuan con la API.
"""
# ===== Importaciones | Aqui se traen los modelos del dominio que usa este modulo. =====
from bongusto.domain.models import Bitacora, PedidoEncabezado, Reserva, Rol, Usuario

# ===== Exportaciones | Define que modelos estaran disponibles cuando otro archivo importe este modulo. =====
__all__ = [
    "Usuario",           # Entidad principal: representa tanto usuarios internos como clientes
    "Rol",               # Define el tipo de usuario y sus permisos dentro del sistema
    "PedidoEncabezado",  # Relaciona los pedidos que ha realizado un usuario
    "Reserva",           # Guarda las reservas hechas por el usuario en el sistema
    "Bitacora",          # Registro historico de acciones realizadas por el usuario
]