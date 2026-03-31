"""
WebSocket consumer para el chat en tiempo real.

Este archivo maneja:
- conexiones WebSocket
- envío y recepción de mensajes
- grupos de usuarios
"""

import json
from types import SimpleNamespace
from urllib.parse import parse_qs

# Permite usar funciones normales (sync) dentro de async
from channels.db import database_sync_to_async
from django.conf import settings
from django.core import signing

# Clase base de Channels para WebSockets
from channels.generic.websocket import AsyncWebsocketConsumer

# Servicio del chat
from bongusto.application.services import ChatService
from bongusto.modules.shared.api_auth import leer_api_token, participante_permitido
from bongusto.domain.models import Usuario


# Instancia del servicio
_chat_service = ChatService()


# Genera el nombre del grupo del chat
def _group_name(participante: str) -> str:

    # Limpia el nombre (solo letras, números, _ o -)
    limpio = "".join(
        ch for ch in (participante or "anonimo").lower()
        if ch.isalnum() or ch in {"_", "-"}
    )

    # Ejemplo: chat_sebastian
    return f"chat_{limpio or 'anonimo'}"



# Consumer principal del chat
class ChatConsumer(AsyncWebsocketConsumer):


    # Se ejecuta cuando alguien se conecta al WebSocket
    async def connect(self):

        # Obtiene el participante desde la URL
        self.participante = self.scope["url_route"]["kwargs"].get(
            "participante",
            "anonimo"
        )

        token = ""
        try:
            raw_query = (self.scope.get("query_string") or b"").decode("utf-8")
            params = parse_qs(raw_query, keep_blank_values=True)
            token = (params.get("token") or [""])[0]
        except Exception:
            token = ""

        usuario = await self._usuario_desde_token_o_sesion(token)
        if not usuario and settings.DEBUG and self.participante == "mesero":
            usuario = SimpleNamespace(
                id_usuario=0,
                tipo_usuario="mesero",
                estado="Activo",
            )

        if not usuario or not participante_permitido(usuario, self.participante):
            await self.close(code=4401)
            return

        self.usuario = usuario

        # Genera el grupo del usuario
        self.group_name = _group_name(self.participante)

        # Une este socket al grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Acepta la conexión
        await self.accept()


    # Se ejecuta cuando se desconecta
    async def disconnect(self, close_code):

        # Lo saca del grupo
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


    # Se ejecuta cuando llega un mensaje desde el frontend
    async def receive(self, text_data):

        # Convierte JSON a diccionario
        data = json.loads(text_data)

        tipo = data.get("tipo", "mensaje")
        remitente = self.participante
        destinatario = data.get("destinatario", "")
        mensaje = data.get("mensaje", "")

        # Validación básica
        if tipo != "mensaje" or not mensaje or not destinatario:
            return

        if not self._destinatario_permitido(destinatario):
            return


        # Guarda el mensaje en base de datos
        # Se usa database_sync_to_async porque el ORM es síncrono
        await database_sync_to_async(
            _chat_service.guardar_mensaje
        )(remitente, destinatario, mensaje)


        # Payload que se va a enviar
        payload = {
            "type": "chat_message",  # nombre del método que se ejecuta abajo
            "tipo": tipo,
            "remitente": remitente,
            "destinatario": destinatario,
            "mensaje": mensaje,
        }

        # Envía al remitente
        await self.channel_layer.group_send(
            _group_name(remitente),
            payload
        )

        # Envía al destinatario
        await self.channel_layer.group_send(
            _group_name(destinatario),
            payload
        )


    # Este método se ejecuta cuando llega un mensaje del grupo
    async def chat_message(self, event):

        # Envía el mensaje al frontend (JavaScript)
        await self.send(
            text_data=json.dumps(
                {
                    "tipo": event["tipo"],
                    "remitente": event["remitente"],
                    "destinatario": event["destinatario"],
                    "mensaje": event["mensaje"],
                }
            )
        )

    @database_sync_to_async
    def _usuario_desde_token_o_sesion(self, token):
        if token:
            try:
                payload = leer_api_token(token)
            except (signing.BadSignature, signing.SignatureExpired):
                return None
            return Usuario.objects.filter(
                pk=payload.get("uid"),
                estado__iexact="activo",
            ).first()

        session = self.scope.get("session")
        if not session:
            return None

        usuario_id = session.get("usuario_id")
        tipo_usuario = (session.get("usuario_tipo") or "").strip().lower()
        if not usuario_id or tipo_usuario not in {"administrador", "mesero"}:
            return None

        return Usuario.objects.filter(
            pk=usuario_id,
            estado__iexact="activo",
        ).first()

    def _destinatario_permitido(self, destinatario):
        destinatario = (destinatario or "").strip().lower()
        tipo_usuario = (getattr(self.usuario, "tipo_usuario", "") or "").strip().lower()

        if tipo_usuario == "cliente":
            return destinatario in {"mesero", "administrador"}
        if tipo_usuario == "mesero":
            return destinatario == "administrador" or destinatario.startswith("cliente_")
        if tipo_usuario == "administrador":
            return destinatario == "mesero" or destinatario.startswith("cliente_")
        return False
