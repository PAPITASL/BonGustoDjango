"""API de pedidos con pasos simples y separados."""

import json
from types import SimpleNamespace

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from bongusto.application.services import PedidoService
from bongusto.domain.models import MensajeChat, Producto, Usuario
from bongusto.modules.shared.api_auth import (
    api_login_required,
    api_owner_or_role,
    resolver_usuario_api,
)
from bongusto.modules.shared.table_state import MesaStateService


_service = PedidoService()
_mesa_service = MesaStateService()


class PedidoApiHelper:
    """Organiza lectura, validacion y conversion de datos."""

    def producto_por_id(self, producto_id):
        return Producto.objects.filter(pk=producto_id).first()

    def usuario_por_id(self, usuario_id):
        return Usuario.objects.filter(pk=usuario_id).first()

    def leer_json(self, request):
        try:
            return json.loads(request.body or "{}"), None
        except json.JSONDecodeError:
            return None, JsonResponse({"error": "JSON invalido"}, status=400)

    def puede_ver_todos(self, request):
        tipo = (request.api_user.tipo_usuario or "").strip().lower()
        return tipo in {"mesero", "administrador"}

    def detalle_to_dict(self, detalle):
        producto = self.producto_por_id(detalle.id_producto)
        cantidad = detalle.cantidad or 0
        precio = float(detalle.precio or 0)
        return {
            "id_detalle": detalle.id_detalle,
            "id_producto": detalle.id_producto,
            "nombre_producto": producto.nombre_producto if producto else f"Producto #{detalle.id_producto}",
            "descripcion_producto": producto.descripcion_producto if producto else "",
            "cantidad": cantidad,
            "precio": precio,
            "subtotal": float(cantidad * precio),
        }

    def pedido_to_dict(self, pedido):
        mesa = _mesa_service.mesa_por_usuario(pedido.id_usuario_id) or {}
        mesa_id = mesa.get("id")
        return {
            "id_pedido": pedido.id_pedido,
            "id_usuario": pedido.id_usuario_id,
            "cliente_nombre": pedido.id_usuario.nombre_completo() if pedido.id_usuario else "",
            "cliente_correo": pedido.id_usuario.correo if pedido.id_usuario else "",
            "mesa_id": mesa_id,
            "mesa_label": f"Mesa {mesa_id}" if mesa_id else "",
            "id_restaurante": pedido.id_restaurante,
            "fecha_pedido": str(pedido.fecha_pedido) if pedido.fecha_pedido else None,
            "total_pedido": float(pedido.total_pedido or 0),
            "estado": "Registrado",
            "items": [self.detalle_to_dict(detalle) for detalle in pedido.pedidodetalle_set.all()],
        }

    def llamado_payload(self, mensaje):
        try:
            payload = json.loads(mensaje.mensaje or "{}")
        except json.JSONDecodeError:
            payload = {"mensaje": mensaje.mensaje or ""}

        return {
            "id": mensaje.id,
            "id_usuario": payload.get("id_usuario"),
            "cliente_nombre": payload.get("cliente_nombre") or mensaje.remitente,
            "mesa_id": payload.get("mesa_id"),
            "mesa_label": payload.get("mesa_label") or (
                f"Mesa {payload.get('mesa_id')}" if payload.get("mesa_id") else "Sin mesa"
            ),
            "mensaje": payload.get("mensaje") or "Cliente solicita mesero",
            "estado": payload.get("estado") or "pendiente",
            "fecha": mensaje.fecha.isoformat() if mensaje.fecha else None,
            "atendido_en": payload.get("atendido_en"),
        }

    def crear_payload_llamado(self, usuario, mensaje):
        mesa = _mesa_service.mesa_por_usuario(usuario.id_usuario) or {}
        mesa_id = mesa.get("id")
        return {
            "tipo": "llamado_mesero",
            "id_usuario": usuario.id_usuario,
            "cliente_nombre": usuario.nombre_completo() or usuario.correo or f"Cliente {usuario.id_usuario}",
            "mesa_id": mesa_id,
            "mesa_label": f"Mesa {mesa_id}" if mesa_id else "Sin mesa asignada",
            "mensaje": (mensaje or "Cliente solicita mesero").strip(),
            "estado": "pendiente",
            "creado_en": timezone.now().isoformat(),
        }


_helper = PedidoApiHelper()


def _usuario_local_desarrollo(tipo_usuario):
    if not settings.DEBUG:
        return None

    tipo = (tipo_usuario or "").strip().lower()
    if tipo == "mesero":
        return SimpleNamespace(id_usuario=0, tipo_usuario="mesero", estado="Activo")
    return None


def _resolver_usuario_llamados(request, *, tipo_desarrollo=None):
    usuario, _, error_response = resolver_usuario_api(request)
    if usuario:
        return usuario, None

    usuario_dev = _usuario_local_desarrollo(tipo_desarrollo)
    if usuario_dev:
        return usuario_dev, None

    return None, error_response


@csrf_exempt
def listar_o_crear(request):
    if request.method == "GET":
        usuario, error_response = _resolver_usuario_llamados(
            request,
            tipo_desarrollo="mesero",
        )
        if error_response:
            return error_response

        request.api_user = usuario
        usuario_id = request.GET.get("id_usuario")

        if usuario_id and not api_owner_or_role(request, usuario_id, roles={"mesero", "administrador"}):
            return JsonResponse({"error": "No autorizado para consultar estos pedidos"}, status=403)

        if not usuario_id and not _helper.puede_ver_todos(request):
            usuario_id = request.api_user.id_usuario

        pedidos = _service.listar_por_usuario(usuario_id) if usuario_id else _service.listar_pedidos()
        return JsonResponse([_helper.pedido_to_dict(pedido) for pedido in pedidos], safe=False)

    if request.method == "POST":
        usuario, _, error_response = resolver_usuario_api(request)
        if error_response:
            return error_response

        request.api_user = usuario
        data, error = _helper.leer_json(request)
        if error:
            return error

        if not api_owner_or_role(request, data.get("id_usuario"), roles={"mesero", "administrador"}):
            return JsonResponse({"error": "No autorizado para crear pedidos a nombre de otro usuario"}, status=403)

        try:
            pedido = _service.crear_pedido_con_detalles(data)
            mesa = _mesa_service.mesa_por_usuario(pedido.id_usuario_id)
            if mesa and mesa.get("id"):
                _mesa_service.actualizar_estado(mesa.get("id"), "con_pedidos")
            return JsonResponse(_helper.pedido_to_dict(pedido), status=201)
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


def detalle(request, pk):
    usuario, error_response = _resolver_usuario_llamados(
        request,
        tipo_desarrollo="mesero",
    )
    if error_response:
        return error_response

    request.api_user = usuario
    pedido = _service.obtener_pedido(pk)
    if not pedido:
        return JsonResponse({"error": "No encontrado"}, status=404)
    return JsonResponse(_helper.pedido_to_dict(pedido))


@csrf_exempt
def llamados_mesero(request):
    if request.method == "GET":
        usuario, error_response = _resolver_usuario_llamados(
            request,
            tipo_desarrollo="mesero",
        )
        if error_response:
            return error_response

        request.api_user = usuario
        if not _helper.puede_ver_todos(request):
            return JsonResponse({"error": "Solo meseros o administradores pueden ver llamados"}, status=403)

        estado = (request.GET.get("estado") or "").strip().lower()
        llamados = MensajeChat.objects.filter(destinatario="mesero_call").order_by("-fecha")
        data = [_helper.llamado_payload(item) for item in llamados]

        if estado:
            data = [item for item in data if item["estado"].lower() == estado]

        return JsonResponse(data, safe=False)

    if request.method == "POST":
        data, error = _helper.leer_json(request)
        if error:
            return error

        usuario_id = data.get("id_usuario")
        usuario, error_response = _resolver_usuario_llamados(request)
        if error_response and not (settings.DEBUG and usuario_id):
            return error_response

        usuario_id = data.get("id_usuario")
        if not usuario_id:
            return JsonResponse({"error": "id_usuario es obligatorio"}, status=400)

        if usuario:
            request.api_user = usuario
            if not api_owner_or_role(request, usuario_id, roles={"mesero", "administrador"}):
                return JsonResponse({"error": "No autorizado para registrar este llamado"}, status=403)

        usuario = _helper.usuario_por_id(usuario_id)
        if not usuario:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)

        payload = _helper.crear_payload_llamado(usuario, data.get("mensaje"))
        llamado = MensajeChat.objects.create(
            remitente=payload["cliente_nombre"],
            destinatario="mesero_call",
            mensaje=json.dumps(payload, ensure_ascii=True),
        )
        return JsonResponse(_helper.llamado_payload(llamado), status=201)

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


@csrf_exempt
def atender_llamado(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, error_response = _resolver_usuario_llamados(
        request,
        tipo_desarrollo="mesero",
    )
    if error_response:
        return error_response

    request.api_user = usuario

    llamado = MensajeChat.objects.filter(pk=pk, destinatario="mesero_call").first()
    if not llamado:
        return JsonResponse({"error": "Llamado no encontrado"}, status=404)

    payload = _helper.llamado_payload(llamado)
    payload["estado"] = "atendido"
    payload["atendido_en"] = timezone.now().isoformat()

    llamado.mensaje = json.dumps(
        {
            "tipo": "llamado_mesero",
            "id_usuario": payload["id_usuario"],
            "cliente_nombre": payload["cliente_nombre"],
            "mesa_id": payload.get("mesa_id"),
            "mesa_label": payload.get("mesa_label"),
            "mensaje": payload["mensaje"],
            "estado": payload["estado"],
            "atendido_en": payload["atendido_en"],
        },
        ensure_ascii=True,
    )
    llamado.save(update_fields=["mensaje"])
    return JsonResponse(_helper.llamado_payload(llamado))
