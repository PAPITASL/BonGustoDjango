"""API de pedidos con pasos simples y separados."""

# Librerias que se usan para leer JSON y crear objetos simples
import json
from types import SimpleNamespace

# Importaciones de Django
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# Servicio principal de pedidos
from bongusto.application.services import PedidoService

# Modelos que se usan en esta API
from bongusto.domain.models import MensajeChat, Producto, Usuario
from bongusto.modules.pedidos.payment_services import SolicitudPagoService

# Funciones de apoyo para autenticacion y permisos
from bongusto.modules.shared.api_auth import (
    api_owner_or_role,
    resolver_usuario_api,
)
from bongusto.modules.shared.audit import registrar_movimiento

# Servicio para manejar el estado de las mesas
from bongusto.modules.shared.table_state import MesaStateService
from bongusto.modules.shared.realtime import emitir_evento_operacion


# Instancias de servicios
_service = PedidoService()
_mesa_service = MesaStateService()
_pago_service = SolicitudPagoService()


class PedidoApiHelper:
    """Organiza lectura, validacion y conversion de datos."""

    # Busca un producto por id
    def producto_por_id(self, producto_id):
        return Producto.objects.filter(pk=producto_id).first()

    # Busca un usuario por id
    def usuario_por_id(self, usuario_id):
        return Usuario.objects.filter(pk=usuario_id).first()

    # Lee el JSON que llega en el request
    def leer_json(self, request):
        try:
            return json.loads(request.body or "{}"), None
        except json.JSONDecodeError:
            return None, JsonResponse({"error": "JSON invalido"}, status=400)

    # Revisa si el usuario puede ver todos los pedidos
    def puede_ver_todos(self, request):
        tipo = (request.api_user.tipo_usuario or "").strip().lower()
        return tipo in {"mesero", "administrador"}

    # Convierte un detalle de pedido a diccionario
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

    # Convierte un pedido completo a diccionario
    def pedido_to_dict(self, pedido):
        mesa_id = getattr(pedido, "mesa_id", None)
        mesa_detalle = _mesa_service.detalle(mesa_id) if mesa_id else None
        mesa_cache = mesa_detalle or {}
        mesa_numero = mesa_cache.get("numero_mesa") or mesa_id
        return {
            "id_pedido": pedido.id_pedido,
            "id_usuario": pedido.id_usuario_id,
            "cliente_nombre": pedido.id_usuario.nombre_completo() if pedido.id_usuario else "",
            "cliente_correo": pedido.id_usuario.correo if pedido.id_usuario else "",
            "mesa_id": mesa_id,
            "mesa_label": (
                "Para llevar"
                if (getattr(pedido, "tipo_pedido", "restaurante") or "").strip().lower() == "para_llevar"
                else mesa_cache.get("etiqueta")
                or (f"Mesa {mesa_numero}" if mesa_numero else "Sin mesa")
            ),
            "id_restaurante": pedido.id_restaurante,
            "tipo_pedido": getattr(pedido, "tipo_pedido", "restaurante"),
            "fecha_pedido": str(pedido.fecha_pedido) if pedido.fecha_pedido else None,
            "total_pedido": float(pedido.total_pedido or 0),
            "estado": getattr(pedido, "estado_pedido", "abierto"),
            "fecha_finalizacion": (
                pedido.fecha_finalizacion.isoformat() if getattr(pedido, "fecha_finalizacion", None) else None
            ),
            "items": [self.detalle_to_dict(detalle) for detalle in pedido.pedidodetalle_set.all()],
        }

    # Convierte un llamado de mesero a diccionario
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
                f"Mesa {payload.get('numero_mesa') or payload.get('mesa_id')}" if payload.get("mesa_id") else "Sin mesa"
            ),
            "mensaje": payload.get("mensaje") or "Cliente solicita mesero",
            "estado": payload.get("estado") or "pendiente",
            "fecha": mensaje.fecha.isoformat() if mensaje.fecha else None,
            "atendido_en": payload.get("atendido_en"),
        }

    # Crea la estructura de datos de un llamado al mesero
    def crear_payload_llamado(self, usuario, mensaje):
        mesa = _mesa_service.mesa_por_usuario(usuario.id_usuario) or {}
        mesa_id = mesa.get("id")
        return {
            "tipo": "llamado_mesero",
            "id_usuario": usuario.id_usuario,
            "cliente_nombre": usuario.nombre_completo() or usuario.correo or f"Cliente {usuario.id_usuario}",
            "mesa_id": mesa_id,
            "mesa_label": mesa.get("etiqueta") or (f"Mesa {mesa_id}" if mesa_id else "Sin mesa asignada"),
            "mensaje": (mensaje or "Cliente solicita mesero").strip(),
            "estado": "pendiente",
            "creado_en": timezone.now().isoformat(),
        }


# Instancia del helper
_helper = PedidoApiHelper()


# Usuario local para pruebas en desarrollo
def _usuario_local_desarrollo(tipo_usuario):
    if not settings.DEBUG:
        return None

    tipo = (tipo_usuario or "").strip().lower()
    if tipo == "mesero":
        return SimpleNamespace(id_usuario=0, tipo_usuario="mesero", estado="Activo")
    return None


# Intenta resolver el usuario real o uno de desarrollo
def _resolver_usuario_llamados(request, *, tipo_desarrollo=None):
    usuario, _, error_response = resolver_usuario_api(request)
    if usuario:
        return usuario, None

    usuario_dev = _usuario_local_desarrollo(tipo_desarrollo)
    if usuario_dev:
        return usuario_dev, None

    return None, error_response


# Esta vista sirve para listar pedidos o crear uno nuevo
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

        # Valida si puede consultar pedidos de otro usuario
        if usuario_id and not api_owner_or_role(request, usuario_id, roles={"mesero", "administrador"}):
            return JsonResponse({"error": "No autorizado para consultar estos pedidos"}, status=403)

        # Si no puede ver todos, solo ve los suyos
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

        # Valida si puede crear pedidos a nombre de otro usuario
        if not api_owner_or_role(request, data.get("id_usuario"), roles={"mesero", "administrador"}):
            return JsonResponse({"error": "No autorizado para crear pedidos a nombre de otro usuario"}, status=403)

        try:
            pedido = _service.crear_pedido_con_detalles(data)
            pedido_payload = _helper.pedido_to_dict(pedido)
            mesa_payload = _mesa_service.detalle(getattr(pedido, "mesa_id", None)) if getattr(pedido, "mesa_id", None) else None
            tipo_usuario = (getattr(request.api_user, "tipo_usuario", "") or "").strip().lower()
            if tipo_usuario in {"administrador", "mesero"}:
                registrar_movimiento(
                    request,
                    (
                        f"Creacion de pedido {pedido.id_pedido} para usuario "
                        f"{pedido.id_usuario_id or '-'} con total {float(pedido.total_pedido or 0):.0f}."
                    ),
                )
            if mesa_payload:
                emitir_evento_operacion("mesa_ocupada", mesa_payload)
                emitir_evento_operacion("estado_mesa_actualizado", mesa_payload)
                emitir_evento_operacion("mesa_actualizada", mesa_payload)
            emitir_evento_operacion("pedido_creado", pedido_payload)
            return JsonResponse(pedido_payload, status=201)
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


# Muestra el detalle de un pedido por id
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
def actualizar_estado_pedido(request, pk):
    """Permite al equipo operativo cambiar el estado de un pedido, incluyendo pedidos para llevar."""
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, error_response = _resolver_usuario_llamados(
        request,
        tipo_desarrollo="mesero",
    )
    if error_response:
        return error_response

    request.api_user = usuario
    if not _helper.puede_ver_todos(request):
        return JsonResponse({"error": "Solo meseros o administradores pueden actualizar pedidos"}, status=403)

    data, error = _helper.leer_json(request)
    if error:
        return error

    estado = (data.get("estado") or "").strip().lower()
    estados_validos = {
        "abierto",
        "en_preparacion",
        "listo_para_recoger",
        "entregado",
        "pagado",
        "finalizado",
    }
    if estado not in estados_validos:
        return JsonResponse({"error": "Estado de pedido no permitido"}, status=400)

    pedido = _service.obtener_pedido(pk)
    if not pedido:
        return JsonResponse({"error": "Pedido no encontrado"}, status=404)

    estado_actual = (getattr(pedido, "estado_pedido", "abierto") or "abierto").strip().lower()
    if estado_actual == "finalizado" and estado != "finalizado":
        return JsonResponse({"error": "El pedido ya fue finalizado"}, status=400)

    pedido.estado_pedido = estado
    if estado == "finalizado":
        pedido.fecha_finalizacion = pedido.fecha_finalizacion or timezone.now()
    pedido.save(update_fields=["estado_pedido", "fecha_finalizacion"])

    payload = _helper.pedido_to_dict(pedido)
    registrar_movimiento(
        request,
        f"Pedido {pedido.id_pedido} actualizado a estado {estado}.",
    )
    emitir_evento_operacion("pedido_actualizado", payload)
    return JsonResponse(payload)


# Esta vista sirve para listar llamados o crear uno nuevo
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

        # Solo meseros o administradores pueden ver llamados
        if not _helper.puede_ver_todos(request):
            return JsonResponse({"error": "Solo meseros o administradores pueden ver llamados"}, status=403)

        estado = (request.GET.get("estado") or "").strip().lower()
        llamados = MensajeChat.objects.filter(destinatario="mesero_call").order_by("-fecha")
        data = [_helper.llamado_payload(item) for item in llamados]

        # Filtra por estado si lo mandan
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

        # Si hay usuario autenticado, valida permisos
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
        llamado_dict = _helper.llamado_payload(llamado)
        emitir_evento_operacion("llamado_creado", llamado_dict)
        return JsonResponse(llamado_dict, status=201)

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


# Marca un llamado como atendido
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

    # Se actualiza el mensaje guardado con el nuevo estado
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
    llamado_dict = _helper.llamado_payload(llamado)
    registrar_movimiento(
        request,
        (
            f"Llamado {llamado.id} marcado como atendido para "
            f"{llamado_dict.get('mesa_label') or 'Sin mesa'}."
        ),
    )
    emitir_evento_operacion("llamado_atendido", llamado_dict)
    return JsonResponse(llamado_dict)


@csrf_exempt
def solicitudes_pago(request):
    """Lista o crea solicitudes de pago coordinadas por BonGusto."""
    if request.method == "GET":
        usuario, error_response = _resolver_usuario_llamados(
            request,
            tipo_desarrollo="mesero",
        )
        if error_response:
            return error_response

        request.api_user = usuario
        if not _helper.puede_ver_todos(request):
            return JsonResponse({"error": "Solo meseros o administradores pueden ver solicitudes de pago"}, status=403)

        estado = request.GET.get("estado")
        return JsonResponse(_pago_service.listar(estado=estado), safe=False)

    if request.method == "POST":
        data, error = _helper.leer_json(request)
        if error:
            return error

        usuario, _, error_response = resolver_usuario_api(request)
        if error_response:
            return error_response

        request.api_user = usuario
        tipo = (usuario.tipo_usuario or "").strip().lower()
        if tipo != "cliente":
            return JsonResponse({"error": "Solo el cliente puede solicitar el pago desde la app"}, status=403)

        try:
            solicitud = _pago_service.crear_solicitud(
                usuario,
                metodo_pago=data.get("metodo_pago"),
                pedido_id=data.get("id_pedido"),
                mesa_id=data.get("mesa_id"),
            )
            payload = _pago_service.solicitud_to_dict(solicitud)
            return JsonResponse(payload, status=201)
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


@csrf_exempt
def actualizar_solicitud_pago(request, pk):
    """Permite que mesero/admin cambien una solicitud a pendiente, atendida o finalizada."""
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, error_response = _resolver_usuario_llamados(
        request,
        tipo_desarrollo="mesero",
    )
    if error_response:
        return error_response

    request.api_user = usuario
    if not _helper.puede_ver_todos(request):
        return JsonResponse({"error": "Solo meseros o administradores pueden actualizar solicitudes de pago"}, status=403)

    data, error = _helper.leer_json(request)
    if error:
        return error

    try:
        solicitud = _pago_service.actualizar_estado(pk, data.get("estado"), mesero=usuario)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    if not solicitud:
        return JsonResponse({"error": "Solicitud de pago no encontrada"}, status=404)

    payload = _pago_service.solicitud_to_dict(solicitud)
    registrar_movimiento(
        request,
        (
            f"Solicitud de pago {solicitud.id_solicitud_pago} marcada como "
            f"{solicitud.estado} para Mesa {solicitud.mesa_id or '-'}."
        ),
    )
    return JsonResponse(payload)
