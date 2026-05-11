"""Broadcast en tiempo real para la cola musical."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone


MUSICA_GROUP = "musica_global"


def emitir_evento_musica(evento, payload=None):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    async_to_sync(channel_layer.group_send)(
        MUSICA_GROUP,
        {
            "type": "musica_push",
            "event_name": (evento or "musica").strip().lower(),
            "payload": payload or {},
            "generated_at": timezone.now().isoformat(),
        },
    )


__all__ = ["MUSICA_GROUP", "emitir_evento_musica"]
