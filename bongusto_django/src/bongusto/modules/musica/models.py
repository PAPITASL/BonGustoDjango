"""Modelos del modulo musica, aqui se agrupan todo lo relacionado con canciones y solicitudes."""

# Se importan los modelos desde la capa de dominio
from bongusto.domain.models import Musica, Reserva, SolicitudMusica

# Aqui se define que modelos se van a usar en este modulo
__all__ = [
    "Musica",
    "SolicitudMusica",
    "Reserva",
]