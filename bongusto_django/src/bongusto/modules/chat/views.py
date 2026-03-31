"""Vistas del modulo chat con una estructura simple."""

import json
from types import SimpleNamespace

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from bongusto.application.services import ChatService
from bongusto.modules.chat.consumers import _group_name
from bongusto.modules.shared.api_auth import participante_permitido, resolver_usuario_api


_service = ChatService()


class ChatPageHelper:
    """Agrupa pasos basicos del chat."""

    def leer_participantes(self, request):
        participante = (request.GET.get("participante") or "administrador").strip()
        conversacion_con = (request.GET.get("con") or "").strip()
        return participante, conversacion_con

    def obtener_mensajes(self, participante, conversacion_con):
        return _service.obtener_conversacion(participante, conversacion_con)

    def mensajes_json(self, mensajes):
        return [
            {
                "id": msg.id,
                "remitente": msg.remitente,
                "destinatario": msg.destinatario,
                "mensaje": msg.mensaje,
                "fecha": msg.fecha.isoformat() if msg.fecha else None,
            }
            for msg in mensajes
        ]

    def destinatario_permitido(self, usuario, destinatario):
        destinatario = (destinatario or "").strip().lower()
        tipo_usuario = (usuario.tipo_usuario or "").strip().lower()

        if tipo_usuario == "cliente":
            return destinatario in {"mesero", "administrador"}
        if tipo_usuario == "mesero":
            return destinatario == "administrador" or destinatario.startswith("cliente_")
        if tipo_usuario == "administrador":
            return destinatario == "mesero" or destinatario.startswith("cliente_")
        return False

    def emitir_tiempo_real(self, remitente, destinatario, mensaje):
        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        payload = {
            "type": "chat_message",
            "tipo": "mensaje",
            "remitente": remitente,
            "destinatario": destinatario,
            "mensaje": mensaje,
        }
        async_to_sync(channel_layer.group_send)(_group_name(remitente), payload)
        async_to_sync(channel_layer.group_send)(_group_name(destinatario), payload)

    def leer_payload_json(self, request):
        try:
            raw_body = (request.body or b"").decode("utf-8").strip()
            if not raw_body:
                return {}
            data = json.loads(raw_body)
            if isinstance(data, dict):
                return data
        except Exception:
            return {}
        return {}


_helper = ChatPageHelper()


def _usuario_chat_desarrollo(participante):
    participante = (participante or "").strip().lower()
    if settings.DEBUG and participante == "mesero":
        return SimpleNamespace(
            id_usuario=0,
            tipo_usuario="mesero",
            estado="Activo",
        )
    return None


def _resolver_usuario_chat(request, participante):
    usuario, _, error_response = resolver_usuario_api(request)
    if usuario:
        return usuario, None

    usuario_dev = _usuario_chat_desarrollo(participante)
    if usuario_dev:
        return usuario_dev, None

    return None, error_response


def index(request):
    participante, conversacion_con = _helper.leer_participantes(request)
    mensajes = _helper.obtener_mensajes(participante, conversacion_con)
    usuario_nombre = request.session.get("usuario_nombre", participante)

    return render(
        request,
        "chat/index.html",
        {
            "mensajes": mensajes,
            "usuario_nombre": usuario_nombre,
            "participante": participante,
            "conversacion_con": conversacion_con,
        },
    )


def api_historial(request):
    participante = (request.GET.get("participante") or "").strip()
    conversacion_con = (request.GET.get("con") or "").strip()

    if not participante:
        return JsonResponse({"error": "participante es obligatorio"}, status=400)

    usuario, error_response = _resolver_usuario_chat(request, participante)
    if error_response:
        return error_response

    if not participante_permitido(usuario, participante):
        return JsonResponse({"error": "No autorizado para consultar este historial"}, status=403)

    mensajes = _helper.obtener_mensajes(participante, conversacion_con)
    return JsonResponse(_helper.mensajes_json(mensajes), safe=False)


def api_enviar(request):
    body_data = _helper.leer_payload_json(request)
    remitente = (
        body_data.get("participante")
        or request.POST.get("participante")
        or request.GET.get("participante")
        or ""
    ).strip().lower()
    destinatario = (
        body_data.get("destinatario")
        or request.POST.get("destinatario")
        or request.GET.get("destinatario")
        or ""
    ).strip().lower()
    mensaje = (
        body_data.get("mensaje")
        or request.POST.get("mensaje")
        or request.GET.get("mensaje")
        or ""
    ).strip()

    if not remitente:
        return JsonResponse({"error": "participante es obligatorio"}, status=400)
    if not destinatario:
        return JsonResponse({"error": "destinatario es obligatorio"}, status=400)
    if not mensaje:
        return JsonResponse({"error": "mensaje es obligatorio"}, status=400)

    usuario, error_response = _resolver_usuario_chat(request, remitente)
    if error_response:
        return error_response

    if not participante_permitido(usuario, remitente):
        return JsonResponse({"error": "No autorizado para usar este participante"}, status=403)
    if not _helper.destinatario_permitido(usuario, destinatario):
        return JsonResponse({"error": "Destinatario no permitido"}, status=403)

    registro = _service.guardar_mensaje(remitente, destinatario, mensaje)
    _helper.emitir_tiempo_real(remitente, destinatario, mensaje)
    return JsonResponse(
        {
            "ok": True,
            "id": registro.id,
            "remitente": remitente,
            "destinatario": destinatario,
            "mensaje": mensaje,
        },
        status=201,
    )
