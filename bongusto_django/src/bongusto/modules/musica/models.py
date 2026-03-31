"""Modelos del modulo musica, aqui se agrupan las entidades relacionadas con canciones y solicitudes del sistema."""

# ===== Importaciones principales | Se traen los modelos desde la capa de dominio. =====
from bongusto.domain.models import Musica, Reserva, SolicitudMusica


# ===== Exportacion de modelos | Se define que modelos quedan disponibles en este modulo. =====
__all__ = [
    "Musica",
    "SolicitudMusica",
    "Reserva",
]