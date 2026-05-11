"""Vistas web y API del modulo de notificaciones."""

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from bongusto.domain.models import NotificacionCliente
from bongusto.modules.notificaciones.services import NotificacionService
from bongusto.modules.shared.api_auth import api_login_required
from bongusto.modules.shared.audit import registrar_movimiento


_service = NotificacionService()


class NotificacionPageHelper:
    """Agrupa pasos pequeños para no repetir código entre web y API."""

    QUICK_TEMPLATES = [
        {
            "titulo": "¡Feliz cumpleaños de parte de BonGusto!",
            "mensaje": "Hoy celebramos contigo. Tienes un detalle especial para disfrutar en tu próxima visita o pedido desde la app.",
            "tipo": "cumpleaños",
        },
        {
            "titulo": "Descuento exclusivo por tiempo limitado",
            "mensaje": "Activa este beneficio desde BonGusto y aprovecha un descuento especial en platos, bebidas o combos seleccionados.",
            "tipo": "promo",
        },
        {
            "titulo": "Estás invitado a una noche especial",
            "mensaje": "Tenemos un evento especial en BonGusto con ambiente, música y una experiencia pensada para que la disfrutes al máximo.",
            "tipo": "evento",
        },
        {
            "titulo": "Un beneficio te está esperando",
            "mensaje": "Queremos verte de nuevo en BonGusto. Por eso activamos una sorpresa especial para tu próxima visita o pedido.",
            "tipo": "beneficio",
        },
        {
            "titulo": "Vuelve a BonGusto con una promo para ti",
            "mensaje": "Hace poco no sabemos de ti y queremos invitarte otra vez. Entra a la app y descubre una promoción pensada para tu regreso.",
            "tipo": "promo",
        },
        {
            "titulo": "Nuevo plan para compartir en BonGusto",
            "mensaje": "Llegó una experiencia nueva al menú con opciones ideales para venir en pareja, con amigos o en celebración especial.",
            "tipo": "general",
        },
    ]

    def listar(self):
        try:
            return _service.listar_todas()
        except Exception:
            return []

    def listar_clientes(self):
        try:
            return _service.listar_clientes_activos()
        except Exception:
            return []

    def buscar(self, pk):
        try:
            return NotificacionCliente.objects.select_related("id_usuario").filter(pk=pk).first()
        except Exception:
            return None

    def render_form(self, request, data=None, error=""):
        data = data or {}
        return render(
            request,
            "notificacion/form.html",
            {
                "clientes": self.listar_clientes(),
                "form_data": {
                    "titulo": data.get("titulo", ""),
                    "mensaje": data.get("mensaje", ""),
                    "tipo": data.get("tipo", "general"),
                    "destino": data.get("destino", "todos"),
                    "id_usuario": str(data.get("id_usuario", "") or ""),
                },
                "error": error,
                "quick_templates": self.QUICK_TEMPLATES,
            },
        )

    def resumen_admin(self):
        try:
            return _service.resumen_admin()
        except Exception:
            return {"total": 0, "pendientes": 0, "leídas": 0, "enviadas_hoy": 0, "tipos": {}}

    def tipo_meta(self, tipo):
        tipo = (tipo or "general").strip().lower()
        metas = {
            "promo": {"label": "Promo", "icon": "fa-bolt", "accent": "#E9C46A", "surface": "#FFF9E7"},
            "evento": {"label": "Evento", "icon": "fa-calendar-star", "accent": "#5DA9E9", "surface": "#EFF7FF"},
            "cumpleaños": {"label": "Cumpleaños", "icon": "fa-cake-candles", "accent": "#F28482", "surface": "#FFF1F5"},
            "beneficio": {"label": "Beneficio", "icon": "fa-gift", "accent": "#43AA8B", "surface": "#ECFBF5"},
            "general": {"label": "General", "icon": "fa-bell", "accent": "#F28482", "surface": "#FFF1F1"},
        }
        return metas.get(tipo, metas["general"])

    def notificacion_to_dict(self, notificacion):
        return {
            "id_notificacion": notificacion.id_notificacion,
            "titulo": notificacion.titulo or "",
            "mensaje": notificacion.mensaje or "",
            "tipo": notificacion.tipo or "general",
            "tipo_meta": self.tipo_meta(notificacion.tipo),
            "leida": bool(notificacion.leida),
            "fecha_envio": notificacion.fecha_envio.isoformat() if notificacion.fecha_envio else None,
            "fecha_lectura": notificacion.fecha_lectura.isoformat() if notificacion.fecha_lectura else None,
        }


_helper = NotificacionPageHelper()


def index(request):
    notificaciones = _helper.listar()
    cards = []
    for item in notificaciones:
        cards.append(
            {
                "item": item,
                "meta": _helper.tipo_meta(item.tipo),
            }
        )
    return render(
        request,
        "notificacion/index.html",
        {
            "notificaciones": cards,
            "resumen": _helper.resumen_admin(),
        },
    )


def create(request):
    return _helper.render_form(request)


def store(request):
    if request.method != "POST":
        return redirect("/notificaciones")

    titulo = (request.POST.get("titulo", "") or "").strip()
    mensaje = (request.POST.get("mensaje", "") or "").strip()
    tipo = (request.POST.get("tipo", "general") or "general").strip().lower()
    destino = (request.POST.get("destino", "todos") or "todos").strip().lower()
    usuario_id = (request.POST.get("id_usuario", "") or "").strip()

    if not titulo:
        return _helper.render_form(request, request.POST, error="Debes escribir un título.")
    if not mensaje:
        return _helper.render_form(request, request.POST, error="Debes escribir el mensaje de la notificación.")

    if destino == "todos":
        total = _service.crear_para_todos(titulo, mensaje, tipo=tipo)
        if total == 0:
            return _helper.render_form(request, request.POST, error="No hay clientes activos para enviar notificaciones.")
        registrar_movimiento(request, f"Envío de notificación masiva '{titulo}' a {total} clientes.")
        return redirect("/notificaciones")

    cliente = None
    if usuario_id.isdigit():
        cliente = next((usuario for usuario in _helper.listar_clientes() if usuario.id_usuario == int(usuario_id)), None)
    if not cliente:
        return _helper.render_form(request, request.POST, error="Debes seleccionar un cliente válido.")

    _service.crear_para_usuario(cliente, titulo, mensaje, tipo=tipo)
    registrar_movimiento(request, f"Envío de notificación '{titulo}' al cliente {cliente.nombre_completo() or cliente.correo or cliente.id_usuario}.")
    return redirect("/notificaciones")


@api_login_required(roles=["cliente"])
def api_listar(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    notificaciones = _service.listar_para_usuario(request.api_user)
    return JsonResponse(
        {
            "items": [_helper.notificacion_to_dict(item) for item in notificaciones],
            "no_leidas": _service.contar_no_leidas(request.api_user),
            "total": len(notificaciones),
        }
    )


@csrf_exempt
@api_login_required(roles=["cliente"])
def api_marcar_leida(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    notificacion = _service.marcar_leida(pk, request.api_user)
    if not notificacion:
        return JsonResponse({"error": "Notificación no encontrada"}, status=404)

    return JsonResponse(
        {
            "ok": True,
            "notificacion": _helper.notificacion_to_dict(notificacion),
            "no_leidas": _service.contar_no_leidas(request.api_user),
        }
    )


@csrf_exempt
@api_login_required(roles=["cliente"])
def api_marcar_todas_leidas(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    actualizadas = _service.marcar_todas_leidas(request.api_user)
    return JsonResponse(
        {
            "ok": True,
            "actualizadas": actualizadas,
            "no_leidas": _service.contar_no_leidas(request.api_user),
        }
    )
