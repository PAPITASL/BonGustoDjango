"""Utilidades de broadcast en tiempo real para operacion de mesas y pedidos."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone


OPERACION_GROUP = "mesas_global"


def emitir_evento_operacion(evento, payload=None):
    """Publica un evento operativo al grupo WebSocket de mesas en vivo."""
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    async_to_sync(channel_layer.group_send)(
        OPERACION_GROUP,
        {
            "type": "operacion_push",
            "event_name": (evento or "operacion").strip().lower(),
            "payload": payload or {},
            "generated_at": timezone.now().isoformat(),
        },
    )


__all__ = ["OPERACION_GROUP", "emitir_evento_operacion"]
