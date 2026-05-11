"""Consumer WebSocket para la cola musical en tiempo real."""

import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core import signing

from bongusto.domain.models import Usuario
from bongusto.modules.musica.realtime import MUSICA_GROUP
from bongusto.modules.musica.services import MusicaService
from bongusto.modules.shared.api_auth import leer_api_token


class MusicaQueueConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self._extraer_token()
        usuario = await self._resolver_usuario(token)
        if not usuario:
            await self.close(code=4401)
            return

        self.usuario = usuario
        await self.channel_layer.group_add(MUSICA_GROUP, self.channel_name)
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {"type": "snapshot", "data": await self._snapshot()},
                ensure_ascii=True,
            )
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(MUSICA_GROUP, self.channel_name)

    async def musica_push(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "event",
                    "event": event.get("event_name") or "musica",
                    "payload": event.get("payload") or {},
                    "generated_at": event.get("generated_at"),
                },
                ensure_ascii=True,
            )
        )

    def _extraer_token(self):
        try:
            raw_query = (self.scope.get("query_string") or b"").decode("utf-8")
            for fragment in raw_query.split("&"):
                if fragment.startswith("token="):
                    return fragment.split("=", 1)[1].strip()
        except Exception:
            return ""
        return ""

    @database_sync_to_async
    def _resolver_usuario(self, token):
        if token:
            try:
                payload = leer_api_token(token)
            except (signing.BadSignature, signing.SignatureExpired):
                payload = None
            if payload:
                usuario = Usuario.objects.filter(
                    pk=payload.get("uid"),
                    estado__iexact="activo",
                ).first()
                if usuario:
                    return usuario

        session = self.scope.get("session")
        if not session:
            return None
        usuario_id = session.get("usuario_id")
        if not usuario_id:
            return None
        return Usuario.objects.filter(pk=usuario_id, estado__iexact="activo").first()

    @database_sync_to_async
    def _snapshot(self):
        return MusicaService().snapshot()


__all__ = ["MusicaQueueConsumer"]
