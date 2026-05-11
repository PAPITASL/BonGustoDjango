"""Modelos del modulo eventos, aqui se agrupan las entidades relacionadas con reservas y eventos del sistema."""

# ===== Importaciones principales | Aqui no creamos modelos nuevos, solo reutilizamos los que ya existen en la capa domain. =====
# Esto ayuda a mantener el proyecto mas ordenado y no duplicar logica
from bongusto.domain.models import PedidoEncabezado, Reserva, Usuario


# ===== Exportacion de modelos | Esto define que modelos se pueden usar cuando otro archivo importa este modulo. =====
# Es como decir: "estos son los modelos importantes de eventos"
__all__ = [
    "Reserva",
    "Usuario",
    "PedidoEncabezado",
]