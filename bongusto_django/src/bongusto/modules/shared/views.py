"""Vistas compartidas enfocadas en tareas de soporte operativo del sistema."""

import json
from time import perf_counter
from types import SimpleNamespace

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from bongusto.domain.models import MensajeChat, PedidoEncabezado, Usuario
from bongusto.modules.shared.api_auth import resolver_usuario_api
from bongusto.modules.shared.audit import registrar_movimiento
from bongusto.modules.shared.realtime import emitir_evento_operacion
from bongusto.modules.shared.table_state import MesaStateService


def home(request):
    """Pagina publica de entrada al ecosistema administrativo de BonGusto."""
    return render(request, "landing.html")


class SharedStatusHelper:
    """Organiza la logica del health check para que quede mas clara y separada."""

    def revisar_base_datos(self):
        """Comprueba si la base de datos responde correctamente."""
        try:
            # Se abre un cursor simple para hacer una consulta minima de prueba.
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True, ""
        except Exception as exc:  # pragma: no cover
            # Si algo falla, se devuelve el error para incluirlo en el estado.
            return False, str(exc)

    def revisar_cache(self):
        """Comprueba si el sistema de cache esta funcionando correctamente."""
        try:
            # Se guarda y se intenta leer un valor temporal para validar que la cache responde.
            marca_tiempo = timezone.now().isoformat()
            cache.set("healthcheck:last_probe", marca_tiempo, timeout=30)
            cache.get("healthcheck:last_probe")
            return True, ""
        except Exception as exc:  # pragma: no cover
            # Si la cache falla, se retorna el mensaje del error detectado.
            return False, str(exc)

    def construir_payload(self, db_ok, db_error, cache_ok, cache_error, elapsed_ms):
        """Arma la respuesta final del health check con todos los datos relevantes."""
        return {
            "status": "ok" if db_ok and cache_ok else "degraded",
            "timestamp": timezone.now().isoformat(),
            "response_time_ms": elapsed_ms,
            "debug": settings.DEBUG,
            "redis_configured": bool(getattr(settings, "REDIS_URL", "")),
            "database": {"ok": db_ok, "error": db_error},
            "cache": {"ok": cache_ok, "error": cache_error},
        }


_helper = SharedStatusHelper()
_mesa_service = MesaStateService()

TRANSLATIONS_ES_EN = {
    "Inicio": "Home",
    "Dashboard": "Dashboard",
    "Usuarios": "Users",
    "Menus": "Menus",
    "Menús": "Menus",
    "Productos": "Products",
    "Música": "Music",
    "Musica": "Music",
    "Eventos": "Events",
    "Notificaciones": "Notifications",
    "Calificaciones": "Ratings",
    "Bitácora": "Audit log",
    "Bitacora": "Audit log",
    "Pedidos": "Orders",
    "Pedido": "Order",
    "Mesas": "Tables",
    "Mesa": "Table",
    "Cliente": "Customer",
    "Clientes": "Customers",
    "Mesero": "Waiter",
    "Meseros": "Waiters",
    "Administrador": "Administrator",
    "Activo": "Active",
    "Activa": "Active",
    "Inactivo": "Inactive",
    "Inactiva": "Inactive",
    "Pendiente": "Pending",
    "Completado": "Completed",
    "Completada": "Completed",
    "Cancelado": "Canceled",
    "Cancelada": "Canceled",
    "Pagado": "Paid",
    "Pagada": "Paid",
    "Disponible": "Available",
    "Ocupada": "Occupied",
    "Ocupado": "Occupied",
    "Feliz cumpleaños": "Happy birthday",
    "Descuento": "Discount",
    "Promoción": "Promotion",
    "Promocion": "Promotion",
    "Evento especial": "Special event",
    "Invitación": "Invitation",
    "Invitacion": "Invitation",
}
TRANSLATIONS_EN_ES = {value: key for key, value in TRANSLATIONS_ES_EN.items()}


def translate_value(value, language):
    """Traduce valores cortos conocidos sin depender de servicios externos."""
    if not isinstance(value, str):
        return value
    cleaned = value.strip()
    if language == "en":
        return TRANSLATIONS_ES_EN.get(cleaned, value)
    return TRANSLATIONS_EN_ES.get(cleaned, value)


def healthcheck(request):
    """Endpoint que revisa rapidamente el estado general del sistema."""
    # Se toma el tiempo de inicio para medir cuanto tarda la validacion.
    started = perf_counter()

    # Se revisan los dos servicios clave: base de datos y cache.
    db_ok, db_error = _helper.revisar_base_datos()
    cache_ok, cache_error = _helper.revisar_cache()

    # Se calcula el tiempo de respuesta en milisegundos.
    elapsed_ms = int((perf_counter() - started) * 1000)

    # Se construye el contenido de la respuesta.
    payload = _helper.construir_payload(db_ok, db_error, cache_ok, cache_error, elapsed_ms)

    # Si alguno de los servicios falla, el estado HTTP cambia a 503.
    status = 200 if db_ok and cache_ok else 503
    return JsonResponse(payload, status=status)


@csrf_exempt
def api_language(request):
    """Guarda o devuelve el idioma actual del usuario."""
    if request.method == "GET":
        return JsonResponse({"language": request.session.get("language", "es")})

    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    try:
        body = json.loads((request.body or b"{}").decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalido"}, status=400)

    language = (body.get("language") or body.get("idioma") or "es").strip().lower()
    if language not in {"es", "en"}:
        return JsonResponse({"error": "Idioma no soportado"}, status=400)

    request.session["language"] = language
    request.session.modified = True
    return JsonResponse({"ok": True, "language": language})


@csrf_exempt
def api_translate(request):
    """Traduce textos comunes usados por las apps y por datos de la base."""
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    try:
        body = json.loads((request.body or b"{}").decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalido"}, status=400)

    language = (body.get("language") or body.get("idioma") or "es").strip().lower()
    if language not in {"es", "en"}:
        return JsonResponse({"error": "Idioma no soportado"}, status=400)

    text = body.get("text")
    texts = body.get("texts")
    if isinstance(texts, list):
        return JsonResponse({"language": language, "texts": [translate_value(item, language) for item in texts]})

    return JsonResponse({"language": language, "text": translate_value(text, language)})


class MesaApiHelper:
    """Agrupa varias ayudas relacionadas con la simulacion compartida de mesas."""

    def leer_json(self, request):
        """Lee el cuerpo JSON de la peticion y devuelve un diccionario limpio."""
        try:
            # Se decodifica el body para intentar convertirlo desde JSON.
            raw_body = (request.body or b"").decode("utf-8").strip()
            if not raw_body:
                return {}
            data = json.loads(raw_body)
            return data if isinstance(data, dict) else {}
        except Exception:
            # Si el body viene vacio o mal formado, se devuelve un diccionario vacio.
            return {}

    def usuario_debug(self, request, body):
        """Permite resolver un usuario de prueba cuando el sistema esta en modo debug."""
        if not settings.DEBUG:
            return None

        # Se intenta leer el id del usuario desde el body o desde la URL.
        usuario_id = body.get("id_usuario") or request.GET.get("id_usuario")
        if not usuario_id:
            # Si no llega un id, se crea un usuario simple de apoyo para pruebas.
            return SimpleNamespace(id_usuario=0, tipo_usuario="mesero", estado="Activo")

        try:
            usuario_id = int(usuario_id)
        except (TypeError, ValueError):
            # Si el id no es valido, se usa igualmente un usuario de prueba.
            return SimpleNamespace(id_usuario=0, tipo_usuario="mesero", estado="Activo")

        # Primero se intenta buscar un usuario activo real.
        usuario = Usuario.objects.filter(pk=usuario_id, estado__iexact="activo").first()
        if usuario:
            return usuario

        # Si no esta activo, al menos se intenta encontrarlo por ID.
        return Usuario.objects.filter(pk=usuario_id).first()

    def resolver_usuario(self, request, body):
        """Resuelve el usuario autenticado usando token o apoyo de debug."""
        # Se intenta autenticar normalmente por API.
        usuario, _, error = resolver_usuario_api(request)
        if usuario:
            return usuario, None

        # Si viene desde interfaz web, intenta resolver por sesion de admin/mesero.
        usuario_sesion = self.usuario_desde_sesion(request)
        if usuario_sesion:
            return usuario_sesion, None

        # Si no se pudo y el sistema esta en debug, se intenta con usuario de desarrollo.
        usuario_dev = self.usuario_debug(request, body)
        if usuario_dev:
            return usuario_dev, None

        return None, error

    def usuario_desde_sesion(self, request):
        """Intenta resolver usuario activo desde la sesion web."""
        usuario_id = request.session.get("usuario_id")
        tipo_usuario = (request.session.get("usuario_tipo") or "").strip().lower()
        if not usuario_id or tipo_usuario not in {"administrador", "mesero"}:
            return None
        return Usuario.objects.filter(pk=usuario_id, estado__iexact="activo").first()

    def puede_ver_mesas(self, usuario):
        """Valida si el usuario tiene permiso para ver el estado general de las mesas."""
        tipo = (getattr(usuario, "tipo_usuario", "") or "").strip().lower()
        return tipo in {"mesero", "administrador"}

    def puede_asignar_mesa(self, usuario):
        """Valida si el usuario tiene permiso para asignarse o asignar una mesa."""
        tipo = (getattr(usuario, "tipo_usuario", "") or "").strip().lower()
        return tipo in {"cliente", "mesero", "administrador"}

    def mesa_payload(self, mesa):
        """Da formato limpio a los datos de una mesa para responder por JSON."""
        return {
            "id": mesa.get("id"),
            "estado": mesa.get("estado") or "disponible",
            "id_usuario": mesa.get("id_usuario"),
            "cliente_nombre": mesa.get("cliente_nombre") or "",
            "cliente_correo": mesa.get("cliente_correo") or "",
            "asignado_en": mesa.get("asignado_en"),
        }


_mesa_helper = MesaApiHelper()


def _resumen_operacion_actual():
    """Construye un snapshot operativo para el modulo de mesas en vivo."""
    mesas = _mesa_service.listar()
    pedidos = list(
        PedidoEncabezado.objects.select_related("id_usuario")
        .prefetch_related("pedidodetalle_set")
        .order_by("-id_pedido")[:40]
    )
    llamados = list(MensajeChat.objects.filter(destinatario="mesero_call").order_by("-fecha")[:40])

    resumen_por_mesa = {}
    mesas_por_id = {}
    for mesa in mesas:
        mesa_id = mesa.get("id")
        if not mesa_id:
            continue
        mesas_por_id[mesa_id] = mesa
        resumen_por_mesa[mesa_id] = {"pedidos": 0, "total": 0.0, "total_pendiente": 0.0}

    for pedido in pedidos:
        usuario = getattr(pedido, "id_usuario", None)
        mesa = _mesa_service.mesa_por_usuario(getattr(usuario, "id_usuario", None) if usuario else None) or {}
        mesa_id = mesa.get("id")
        mesa_actual = mesas_por_id.get(mesa_id) or {}
        estado_mesa = (mesa_actual.get("estado") or "").strip().lower()
        pedido_actual_id = mesa_actual.get("pedido_actual_id") or mesa_actual.get("pedido_actual")
        total = float(pedido.total_pedido or 0)
        if (
            mesa_id in resumen_por_mesa
            and pedido_actual_id
            and int(pedido_actual_id) == int(pedido.id_pedido)
            and estado_mesa not in {"libre", "bloqueada", "disponible"}
        ):
            resumen_por_mesa[mesa_id]["pedidos"] += 1
            resumen_por_mesa[mesa_id]["total"] += total
            resumen_por_mesa[mesa_id]["total_pendiente"] += total

    llamados_pendientes = 0
    for llamado in llamados:
        try:
            payload = json.loads(llamado.mensaje or "{}")
            estado = (payload.get("estado") or "pendiente").strip().lower()
        except Exception:
            estado = "pendiente"
        if estado == "pendiente":
            llamados_pendientes += 1

    return {
        "mesas": mesas,
        "resumen_por_mesa": resumen_por_mesa,
        "ultimos_pedidos": pedidos[:12],
        "kpis": {
            "mesas_totales": len(mesas),
            "mesas_ocupadas": sum(1 for mesa in mesas if (mesa.get("estado") or "").strip().lower() != "disponible"),
            "pedidos_totales": len(pedidos),
            "llamados_pendientes": llamados_pendientes,
        },
    }


def mesas_index(request):
    """Modulo web para que administrador/mesero monitoreen mesas en tiempo real."""
    if not request.session.get("usuario_id"):
        return redirect("/login")

    tipo_usuario = (request.session.get("usuario_tipo") or "").strip().lower()
    if tipo_usuario not in {"administrador", "mesero"}:
        return redirect("/dashboard")

    contexto = _resumen_operacion_actual()
    return render(request, "mesa/index.html", contexto)


@csrf_exempt
def api_mesas(request):
    """Devuelve la lista completa de mesas simuladas."""
    # Esta vista solo acepta consultas GET.
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    # Se intenta leer el body y resolver el usuario autenticado.
    body = _mesa_helper.leer_json(request)
    usuario, error = _mesa_helper.resolver_usuario(request, body)
    if error:
        return error

    # Solo meseros y administradores pueden ver todas las mesas.
    if not _mesa_helper.puede_ver_mesas(usuario):
        return JsonResponse({"error": "Solo meseros o administradores pueden ver las mesas"}, status=403)

    # Se listan las mesas y se convierten a un formato JSON limpio.
    mesas = [_mesa_helper.mesa_payload(mesa) for mesa in _mesa_service.listar()]
    return JsonResponse(mesas, safe=False)


@csrf_exempt
def api_asignar_mesa(request):
    """Asigna una mesa disponible al usuario actual."""
    # Esta vista solo acepta peticiones POST.
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    # Se obtiene la informacion enviada y el usuario autenticado.
    body = _mesa_helper.leer_json(request)
    usuario, error = _mesa_helper.resolver_usuario(request, body)
    if error:
        return error

    # Se valida si el usuario tiene permiso para este proceso.
    if not _mesa_helper.puede_asignar_mesa(usuario):
        return JsonResponse({"error": "No autorizado para asignar mesa"}, status=403)

    # Se intenta asignar una mesa libre.
    mesa = _mesa_service.asignar_a_usuario(usuario)
    if not mesa:
        return JsonResponse({"error": "No hay mesas disponibles en este momento"}, status=409)

    registrar_movimiento(
        request,
        (
            f"Asignacion de mesa {mesa.get('id')} a usuario "
            f"{getattr(usuario, 'id_usuario', '-')}."
        ),
    )
    emitir_evento_operacion("mesa_asignada", _mesa_helper.mesa_payload(mesa))
    return JsonResponse(_mesa_helper.mesa_payload(mesa), status=201)


@csrf_exempt
def api_mi_mesa(request):
    """Devuelve la mesa actualmente asignada al usuario autenticado."""
    # Solo se permite consulta GET.
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    # Se resuelve el usuario para saber cual es su mesa.
    body = _mesa_helper.leer_json(request)
    usuario, error = _mesa_helper.resolver_usuario(request, body)
    if error:
        return error

    # Se busca la mesa asociada a ese usuario.
    mesa = _mesa_service.mesa_por_usuario(usuario.id_usuario)
    if not mesa:
        return JsonResponse({"error": "El usuario no tiene mesa asignada"}, status=404)

    return JsonResponse(_mesa_helper.mesa_payload(mesa))


@csrf_exempt
def api_actualizar_mesa(request, mesa_id):
    """Actualiza manualmente el estado de una mesa especifica."""
    # Esta operacion modifica informacion, por eso se maneja con POST.
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    # Se lee el contenido enviado y se resuelve el usuario.
    body = _mesa_helper.leer_json(request)
    usuario, error = _mesa_helper.resolver_usuario(request, body)
    if error:
        return error

    # Solo meseros y administradores pueden actualizar estados de mesas.
    if not _mesa_helper.puede_ver_mesas(usuario):
        return JsonResponse({"error": "Solo meseros o administradores pueden actualizar mesas"}, status=403)

    # Se intenta actualizar la mesa con el nuevo estado enviado.
    mesa = _mesa_service.actualizar_estado(mesa_id, body.get("estado"))
    if not mesa:
        return JsonResponse({"error": "Mesa o estado no valido"}, status=400)

    registrar_movimiento(
        request,
        (
            f"Actualizacion de estado de mesa {mesa_id} a "
            f"{(body.get('estado') or '').strip() or 'sin_estado'}."
        ),
    )
    emitir_evento_operacion("mesa_actualizada", _mesa_helper.mesa_payload(mesa))
    return JsonResponse(_mesa_helper.mesa_payload(mesa))
