"""Consumer WebSocket para monitoreo operativo en vivo (mesas y pedidos)."""

import json
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core import signing

from bongusto.domain.models import Usuario
from bongusto.modules.mesas.services import OperacionMesasService
from bongusto.modules.shared.api_auth import leer_api_token
from bongusto.modules.shared.realtime import OPERACION_GROUP
from bongusto.modules.shared.table_state import MesaStateService


class OperacionMesasConsumer(AsyncWebsocketConsumer):
    """Canal de tiempo real para que admin y mesero vean operacion en vivo."""

    async def connect(self):
        token = self._extraer_token_query()
        usuario = await self._usuario_desde_token_o_sesion(token)
        if not usuario:
            await self.close(code=4401)
            return

        self.usuario = usuario
        self.tipo_usuario = (getattr(usuario, "tipo_usuario", "") or "").strip().lower()
        self.group_name = OPERACION_GROUP

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        snapshot = await self._snapshot_operacion()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "snapshot",
                    "data": snapshot,
                },
                ensure_ascii=True,
            )
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def operacion_push(self, event):
        if self.tipo_usuario == "cliente":
            permitido = await self._evento_permitido_cliente(event.get("payload") or {})
            if not permitido:
                return

        await self.send(
            text_data=json.dumps(
                {
                    "type": "event",
                    "event": event.get("event_name") or "operacion",
                    "payload": event.get("payload") or {},
                    "generated_at": event.get("generated_at"),
                },
                ensure_ascii=True,
            )
        )

    def _extraer_token_query(self):
        try:
            raw_query = (self.scope.get("query_string") or b"").decode("utf-8")
            params = parse_qs(raw_query, keep_blank_values=True)
            token = (params.get("token") or [""])[0].strip()
            return token.replace("#", "").replace("'", "").replace('"', "")
        except Exception:
            return ""

    @database_sync_to_async
    def _usuario_desde_token_o_sesion(self, token):
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

        return self._usuario_desde_sesion_sync()

    def _usuario_desde_sesion_sync(self):
        session = self.scope.get("session")
        if not session:
            return None

        usuario_id = session.get("usuario_id")
        tipo_usuario = (session.get("usuario_tipo") or "").strip().lower()
        if not usuario_id or tipo_usuario not in {"administrador", "mesero"}:
            return None

        return Usuario.objects.filter(pk=usuario_id, estado__iexact="activo").first()

    @database_sync_to_async
    def _snapshot_operacion(self):
        service = OperacionMesasService()
        return service.snapshot_para_usuario(self.usuario)

    @database_sync_to_async
    def _evento_permitido_cliente(self, payload):
        usuario_id = getattr(self.usuario, "id_usuario", None)
        if not usuario_id:
            return False
        mesa_usuario = MesaStateService().mesa_por_usuario(usuario_id) or {}
        mesa_id = mesa_usuario.get("id")
        if payload.get("id_usuario") == usuario_id:
            return True
        if payload.get("cliente_id") == usuario_id:
            return True
        if mesa_id and payload.get("mesa_id") == mesa_id:
            return True
        if mesa_id and payload.get("id") == mesa_id:
            return True
        if payload.get("id") and payload.get("id_usuario") is None:
            return False
        return False


__all__ = ["OperacionMesasConsumer"]
