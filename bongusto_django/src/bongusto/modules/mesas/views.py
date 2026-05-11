"""Vistas web y API del modulo mesas."""

import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from bongusto.domain.models import SolicitudPago, Usuario
from bongusto.modules.mesas.forms import MesaForm
from bongusto.modules.mesas.models import Mesa
from bongusto.modules.mesas.services import OperacionMesasService
from bongusto.modules.pedidos.payment_services import SolicitudPagoService
from bongusto.modules.shared.api_auth import resolver_usuario_api
from bongusto.modules.shared.audit import registrar_movimiento
from bongusto.modules.shared.realtime import emitir_evento_operacion
from bongusto.modules.shared.table_state import MesaStateService


_operacion_service = OperacionMesasService()
_mesa_service = MesaStateService()
_pago_service = SolicitudPagoService()


def _leer_json(request):
    try:
        return json.loads((request.body or b"{}").decode("utf-8")), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "JSON invalido"}, status=400)


def _usuario_desde_sesion(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None
    return Usuario.objects.filter(pk=usuario_id, estado__iexact="activo").first()


def _resolver_usuario_hibrido(request):
    usuario, _, error = resolver_usuario_api(request)
    if usuario:
        return usuario, None

    usuario_sesion = _usuario_desde_sesion(request)
    if usuario_sesion:
        return usuario_sesion, None

    return None, error or JsonResponse({"error": "Autenticacion requerida"}, status=401)


def _es_admin(usuario):
    return (getattr(usuario, "tipo_usuario", "") or "").strip().lower() == "administrador"


def _es_operativo(usuario):
    return (getattr(usuario, "tipo_usuario", "") or "").strip().lower() in {"administrador", "mesero"}


def _emitir_cambio_mesa(evento, mesa_payload):
    if not mesa_payload:
        return
    emitir_evento_operacion(evento, mesa_payload)
    if evento != "mesa_actualizada":
        emitir_evento_operacion("mesa_actualizada", mesa_payload)
    emitir_evento_operacion("estado_mesa_actualizado", mesa_payload)


def _solicitud_activa_mesa(mesa_id):
    return (
        SolicitudPago.objects.select_related("id_pedido", "id_usuario", "atendido_por")
        .filter(mesa_id=mesa_id)
        .exclude(estado="finalizada")
        .order_by("-fecha_creacion")
        .first()
    )


def _contexto_gestion(request, *, form=None, gestion_error="", gestion_ok=""):
    usuario = _usuario_desde_sesion(request)
    snapshot = _operacion_service.snapshot_para_usuario(usuario) if usuario else {
        "kpis": {},
        "mesas": [],
        "resumen_por_mesa": {},
        "ultimos_pedidos": [],
        "llamados": [],
        "solicitudes_pago": [],
    }
    mesas_catalogo = _mesa_service.listar_modelos(incluir_inactivas=True)
    mesa_edicion = None

    edit_id = request.GET.get("edit")
    if edit_id:
        mesa_edicion = _mesa_service.buscar_modelo(edit_id)
        if mesa_edicion and form is None:
            form = MesaForm(instance=mesa_edicion)

    if form is None:
        form = MesaForm()

    snapshot.update(
        {
            "mesas_catalogo": mesas_catalogo,
            "form": form,
            "mesa_edicion": mesa_edicion,
            "gestion_error": gestion_error,
            "gestion_ok": gestion_ok,
        }
    )
    return snapshot


def index(request):
    usuario = _usuario_desde_sesion(request)
    if not usuario:
        return redirect("/login")

    if not _es_operativo(usuario):
        return redirect("/dashboard")

    registrar_movimiento(request, "Ingreso al modulo Mesas.")
    return render(request, "mesa/index.html", _contexto_gestion(request))


def store(request):
    usuario = _usuario_desde_sesion(request)
    if not usuario or not _es_admin(usuario):
        return redirect("/mesas")

    if request.method != "POST":
        return redirect("/mesas")

    form = MesaForm(request.POST)
    if not form.is_valid():
        return render(request, "mesa/index.html", _contexto_gestion(request, form=form, gestion_error="Revisa los datos de la nueva mesa."))

    mesa = form.save(commit=False)
    mesa.estado = Mesa.ESTADO_LIBRE if mesa.activa else Mesa.ESTADO_BLOQUEADA
    mesa.save()
    registrar_movimiento(request, f"Creacion de mesa {mesa.numero_mesa}.")
    payload = _mesa_service.detalle(mesa.id)
    _emitir_cambio_mesa("mesa_creada", payload)
    return redirect("/mesas")


def update(request, pk):
    usuario = _usuario_desde_sesion(request)
    if not usuario or not _es_admin(usuario):
        return redirect("/mesas")

    mesa = _mesa_service.buscar_modelo(pk)
    if not mesa:
        return redirect("/mesas")

    if request.method != "POST":
        return redirect(f"/mesas?edit={pk}")

    form = MesaForm(request.POST, instance=mesa)
    if not form.is_valid():
        return render(
            request,
            "mesa/index.html",
            _contexto_gestion(request, form=form, gestion_error="No se pudo actualizar la mesa."),
        )

    mesa = form.save(commit=False)
    if not mesa.activa and mesa.estado == Mesa.ESTADO_LIBRE:
        mesa.estado = Mesa.ESTADO_BLOQUEADA
    elif mesa.activa and mesa.estado == Mesa.ESTADO_BLOQUEADA and not mesa.pedido_actual_id:
        mesa.estado = Mesa.ESTADO_LIBRE
    mesa.save()
    registrar_movimiento(request, f"Actualizacion de mesa {mesa.numero_mesa}.")
    payload = _mesa_service.detalle(mesa.id)
    _emitir_cambio_mesa("mesa_editada", payload)
    return redirect("/mesas")


def toggle(request, pk):
    usuario = _usuario_desde_sesion(request)
    if not usuario or not _es_admin(usuario) or request.method != "POST":
        return redirect("/mesas")

    mesa = _mesa_service.buscar_modelo(pk)
    if not mesa:
        return redirect("/mesas")

    try:
        if mesa.activa:
            _mesa_service.bloquear(mesa)
            evento = "mesa_desactivada"
            accion = f"Desactivacion de mesa {mesa.numero_mesa}."
        else:
            _mesa_service.reactivar(mesa)
            evento = "mesa_reactivada"
            accion = f"Reactivacion de mesa {mesa.numero_mesa}."
    except Exception as exc:
        return render(request, "mesa/index.html", _contexto_gestion(request, gestion_error=str(exc)))

    registrar_movimiento(request, accion)
    payload = _mesa_service.detalle(mesa.id)
    _emitir_cambio_mesa(evento, payload)
    return redirect("/mesas")


def delete(request, pk):
    usuario = _usuario_desde_sesion(request)
    if not usuario or not _es_admin(usuario) or request.method != "POST":
        return redirect("/mesas")

    mesa = _mesa_service.buscar_modelo(pk)
    if not mesa:
        return redirect("/mesas")

    if mesa.estado != Mesa.ESTADO_BLOQUEADA or mesa.activa:
        try:
            _mesa_service.bloquear(mesa, motivo="Preparada para eliminacion definitiva.")
            registrar_movimiento(request, f"Bloqueo previo a eliminacion de mesa {mesa.numero_mesa}.")
            payload = _mesa_service.detalle(mesa.id)
            _emitir_cambio_mesa("mesa_desactivada", payload)
            return render(
                request,
                "mesa/index.html",
                _contexto_gestion(
                    request,
                    gestion_ok="Mesa bloqueada. Vuelve a presionar eliminar definitivamente para borrarla por completo.",
                ),
            )
        except Exception as exc:
            return render(request, "mesa/index.html", _contexto_gestion(request, gestion_error=str(exc)))

    if _mesa_service.tiene_historial(mesa):
        mesa.delete()
        registrar_movimiento(request, f"Eliminacion definitiva de mesa {mesa.numero_mesa} con historial.")
        _emitir_cambio_mesa("mesa_eliminada", {"id": pk, "numero_mesa": mesa.numero_mesa, "estado": "eliminada"})
        return render(
            request,
            "mesa/index.html",
            _contexto_gestion(request, gestion_ok="Mesa con actividad historica eliminada definitivamente."),
        )

    mesa.delete()
    registrar_movimiento(request, f"Eliminacion definitiva de mesa {mesa.numero_mesa}.")
    _emitir_cambio_mesa("mesa_eliminada", {"id": pk, "numero_mesa": mesa.numero_mesa, "estado": "eliminada"})
    return render(request, "mesa/index.html", _contexto_gestion(request, gestion_ok="Mesa eliminada definitivamente."))


@csrf_exempt
def api_listar(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, error = _resolver_usuario_hibrido(request)
    if error:
        return error

    incluir_inactivas = _es_operativo(usuario) and request.GET.get("incluir_inactivas") == "1"
    mesas = _mesa_service.listar(incluir_inactivas=incluir_inactivas)
    if not _es_operativo(usuario):
        mesas = [mesa for mesa in mesas if mesa.get("activa")]
    return JsonResponse(mesas, safe=False)


@csrf_exempt
def api_estado(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, error = _resolver_usuario_hibrido(request)
    if error:
        return error

    mesas = _mesa_service.listar(incluir_inactivas=_es_operativo(usuario))
    payload = [
        {
            "id": mesa["id"],
            "numero_mesa": mesa["numero_mesa"],
            "estado": mesa["estado"],
            "activa": mesa["activa"],
            "pedido_activo_id": mesa.get("pedido_activo_id"),
        }
        for mesa in mesas
        if _es_operativo(usuario) or mesa.get("activa")
    ]
    return JsonResponse(payload, safe=False)


@csrf_exempt
def api_detalle(request, pk):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, error = _resolver_usuario_hibrido(request)
    if error:
        return error

    mesa = _mesa_service.detalle(pk)
    if not mesa:
        return JsonResponse({"error": "Mesa no encontrada"}, status=404)
    if not _es_operativo(usuario) and not mesa.get("activa"):
        return JsonResponse({"error": "Mesa no disponible"}, status=404)
    return JsonResponse(mesa)


@csrf_exempt
def api_snapshot(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, error = _resolver_usuario_hibrido(request)
    if error:
        return error

    return JsonResponse(_operacion_service.snapshot_para_usuario(usuario))


@csrf_exempt
def api_asignar_mesa(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    data, error = _leer_json(request)
    if error:
        return error

    usuario, auth_error = _resolver_usuario_hibrido(request)
    if auth_error:
        return auth_error

    mesa_id = data.get("mesa_id")
    numero_mesa = data.get("numero_mesa")
    codigo_mesa = data.get("codigo_mesa")
    if not numero_mesa and codigo_mesa:
        digitos = "".join(ch for ch in str(codigo_mesa) if ch.isdigit())
        numero_mesa = int(digitos) if digitos else None

    try:
        mesa = _mesa_service.seleccionar_para_cliente(
            usuario,
            mesa_id=mesa_id,
            numero_mesa=numero_mesa,
        )
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    payload = _mesa_service.detalle(mesa.id)
    registrar_movimiento(request, f"Asignacion de mesa {payload.get('numero_mesa')} a usuario {usuario.id_usuario}.")
    _emitir_cambio_mesa("mesa_ocupada", payload)
    return JsonResponse(payload, status=201)


@csrf_exempt
def api_mi_mesa(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, error = _resolver_usuario_hibrido(request)
    if error:
        return error

    mesa = _mesa_service.mesa_por_usuario(usuario.id_usuario)
    if not mesa:
        return JsonResponse({"error": "El usuario no tiene mesa asignada"}, status=404)
    return JsonResponse(mesa)


@csrf_exempt
def api_actualizar_mesa(request, mesa_id):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    data, error = _leer_json(request)
    if error:
        return error

    usuario, auth_error = _resolver_usuario_hibrido(request)
    if auth_error:
        return auth_error
    if not _es_operativo(usuario):
        return JsonResponse({"error": "No autorizado"}, status=403)

    accion = (data.get("estado") or "").strip().lower()
    try:
        if accion in {"libre", "disponible"}:
            mesa = _mesa_service.detalle(_mesa_service.liberar(mesa_id, forzada=False, mesero=usuario).id)
            evento = "mesa_liberada"
        elif accion in {"bloqueada", "inactiva", "deshabilitada"}:
            mesa = _mesa_service.detalle(_mesa_service.bloquear(mesa_id).id)
            evento = "mesa_bloqueada"
        elif accion == "en_limpieza":
            mesa = _mesa_service.detalle(_mesa_service.marcar_en_limpieza(mesa_id, mesero=usuario).id)
            evento = "mesa_actualizada"
        elif accion == "reactivar":
            mesa = _mesa_service.detalle(_mesa_service.reactivar(mesa_id).id)
            evento = "mesa_reactivada"
        else:
            mesa_modelo = _mesa_service.actualizar_estado(mesa_id, accion)
            if not mesa_modelo:
                return JsonResponse({"error": "Mesa o estado no valido"}, status=400)
            mesa = _mesa_service.detalle(mesa_modelo.id)
            evento = "mesa_actualizada"
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    registrar_movimiento(request, f"Actualizacion de estado de mesa {mesa.get('numero_mesa')} a {mesa.get('estado')}.")
    _emitir_cambio_mesa(evento, mesa)
    return JsonResponse(mesa)


@csrf_exempt
def api_solicitar_pago_mesa(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    data, error = _leer_json(request)
    if error:
        return error

    usuario, auth_error = _resolver_usuario_hibrido(request)
    if auth_error:
        return auth_error

    mesa = _mesa_service.buscar_modelo(pk)
    if not mesa or not mesa.activa:
        return JsonResponse({"error": "Mesa no disponible"}, status=404)

    try:
        solicitud = _pago_service.crear_solicitud(
            usuario,
            metodo_pago=data.get("metodo_pago"),
            pedido_id=data.get("id_pedido"),
            mesa_id=mesa.id,
        )
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    payload = _pago_service.solicitud_to_dict(solicitud)
    return JsonResponse(payload, status=201)


@csrf_exempt
def api_confirmar_pago_mesa(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, auth_error = _resolver_usuario_hibrido(request)
    if auth_error:
        return auth_error
    if not _es_operativo(usuario):
        return JsonResponse({"error": "No autorizado"}, status=403)

    solicitud = _solicitud_activa_mesa(pk)
    if not solicitud:
        return JsonResponse({"error": "La mesa no tiene una solicitud de pago pendiente"}, status=404)

    try:
        solicitud = _pago_service.actualizar_estado(solicitud.id_solicitud_pago, "finalizada", mesero=usuario)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    mesa_payload = _mesa_service.detalle(pk)
    registrar_movimiento(request, f"Pago confirmado para mesa {mesa_payload.get('numero_mesa')}.")
    return JsonResponse({"solicitud": _pago_service.solicitud_to_dict(solicitud), "mesa": mesa_payload})


@csrf_exempt
def api_liberar_mesa(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, auth_error = _resolver_usuario_hibrido(request)
    if auth_error:
        return auth_error
    if not _es_operativo(usuario):
        return JsonResponse({"error": "No autorizado"}, status=403)

    data, error = _leer_json(request)
    if error:
        return error

    mesa_actual = _mesa_service.buscar_modelo(pk)
    forzada = bool(data.get("forzada")) if isinstance(data, dict) else False
    if (
        not forzada
        and _es_admin(usuario)
        and mesa_actual
        and mesa_actual.estado in {Mesa.ESTADO_ESPERANDO_PAGO, Mesa.ESTADO_PAGADA, Mesa.ESTADO_EN_LIMPIEZA}
    ):
        forzada = True
    try:
        mesa = _mesa_service.liberar(pk, forzada=forzada, mesero=usuario)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    payload = _mesa_service.detalle(mesa.id)
    registrar_movimiento(
        request,
        f"{'Liberacion manual' if forzada and _es_admin(usuario) else 'Liberacion'} de mesa {payload.get('numero_mesa')}.",
    )
    _emitir_cambio_mesa("mesa_liberada", payload)
    return JsonResponse(payload)


@csrf_exempt
def api_limpiar_cache_mesas(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, auth_error = _resolver_usuario_hibrido(request)
    if auth_error:
        return auth_error
    if not _es_admin(usuario):
        return JsonResponse({"error": "Solo el administrador puede limpiar el estado de mesas"}, status=403)

    mesas = _mesa_service.limpiar_cache_operacion()
    snapshot = _operacion_service.snapshot_para_usuario(usuario)
    for mesa in mesas:
        _emitir_cambio_mesa("mesa_actualizada", mesa)
    registrar_movimiento(request, "Reconstruccion del estado operativo de mesas y limpieza de cache.")
    return JsonResponse({"ok": True, "snapshot": snapshot, "mesas": mesas})


@csrf_exempt
def api_bloquear_mesa(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, auth_error = _resolver_usuario_hibrido(request)
    if auth_error:
        return auth_error
    if not _es_admin(usuario):
        return JsonResponse({"error": "Solo el administrador puede bloquear mesas"}, status=403)

    try:
        mesa = _mesa_service.bloquear(pk)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    payload = _mesa_service.detalle(mesa.id)
    registrar_movimiento(request, f"Bloqueo de mesa {payload.get('numero_mesa')}.")
    _emitir_cambio_mesa("mesa_bloqueada", payload)
    return JsonResponse(payload)


@csrf_exempt
def api_activar_mesa(request, pk):
    return api_reactivar_mesa(request, pk)


@csrf_exempt
def api_reactivar_mesa(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, auth_error = _resolver_usuario_hibrido(request)
    if auth_error:
        return auth_error
    if not _es_admin(usuario):
        return JsonResponse({"error": "Solo el administrador puede reactivar mesas"}, status=403)

    try:
        mesa = _mesa_service.reactivar(pk)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    payload = _mesa_service.detalle(mesa.id)
    registrar_movimiento(request, f"Reactivacion de mesa {payload.get('numero_mesa')}.")
    _emitir_cambio_mesa("mesa_reactivada", payload)
    return JsonResponse(payload)


@csrf_exempt
def api_desactivar_mesa(request, pk):
    return api_bloquear_mesa(request, pk)


@csrf_exempt
def api_historial_mesa(request, pk):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, auth_error = _resolver_usuario_hibrido(request)
    if auth_error:
        return auth_error
    if not _es_operativo(usuario):
        return JsonResponse({"error": "No autorizado"}, status=403)

    historial = _mesa_service.historial(pk)
    if not historial:
        return JsonResponse({"error": "Mesa no encontrada"}, status=404)
    return JsonResponse(historial)


__all__ = [
    "index",
    "store",
    "update",
    "toggle",
    "delete",
    "api_listar",
    "api_estado",
    "api_detalle",
    "api_snapshot",
    "api_asignar_mesa",
    "api_mi_mesa",
    "api_actualizar_mesa",
    "api_solicitar_pago_mesa",
    "api_confirmar_pago_mesa",
    "api_liberar_mesa",
    "api_limpiar_cache_mesas",
    "api_bloquear_mesa",
    "api_activar_mesa",
    "api_desactivar_mesa",
    "api_reactivar_mesa",
    "api_historial_mesa",
]
