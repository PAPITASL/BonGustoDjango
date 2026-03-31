"""Vistas compartidas de soporte operativo."""

import json
from time import perf_counter
from types import SimpleNamespace

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from bongusto.domain.models import Usuario
from bongusto.modules.shared.api_auth import resolver_usuario_api
from bongusto.modules.shared.table_state import MesaStateService


class SharedStatusHelper:
    """Separa los pasos del health check para que sean faciles de leer."""

    def revisar_base_datos(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True, ""
        except Exception as exc:  # pragma: no cover
            return False, str(exc)

    def revisar_cache(self):
        try:
            marca_tiempo = timezone.now().isoformat()
            cache.set("healthcheck:last_probe", marca_tiempo, timeout=30)
            cache.get("healthcheck:last_probe")
            return True, ""
        except Exception as exc:  # pragma: no cover
            return False, str(exc)

    def construir_payload(self, db_ok, db_error, cache_ok, cache_error, elapsed_ms):
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


def healthcheck(request):
    started = perf_counter()
    db_ok, db_error = _helper.revisar_base_datos()
    cache_ok, cache_error = _helper.revisar_cache()
    elapsed_ms = int((perf_counter() - started) * 1000)
    payload = _helper.construir_payload(db_ok, db_error, cache_ok, cache_error, elapsed_ms)
    status = 200 if db_ok and cache_ok else 503
    return JsonResponse(payload, status=status)


class MesaApiHelper:
    """Agrupa la simulacion compartida de mesas."""

    def leer_json(self, request):
        try:
            raw_body = (request.body or b"").decode("utf-8").strip()
            if not raw_body:
                return {}
            data = json.loads(raw_body)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def usuario_debug(self, request, body):
        if not settings.DEBUG:
            return None

        usuario_id = body.get("id_usuario") or request.GET.get("id_usuario")
        if not usuario_id:
            return SimpleNamespace(id_usuario=0, tipo_usuario="mesero", estado="Activo")

        try:
            usuario_id = int(usuario_id)
        except (TypeError, ValueError):
            return SimpleNamespace(id_usuario=0, tipo_usuario="mesero", estado="Activo")

        usuario = Usuario.objects.filter(pk=usuario_id, estado__iexact="activo").first()
        if usuario:
            return usuario

        return Usuario.objects.filter(pk=usuario_id).first()

    def resolver_usuario(self, request, body):
        usuario, _, error = resolver_usuario_api(request)
        if usuario:
            return usuario, None

        usuario_dev = self.usuario_debug(request, body)
        if usuario_dev:
            return usuario_dev, None

        return None, error

    def puede_ver_mesas(self, usuario):
        tipo = (getattr(usuario, "tipo_usuario", "") or "").strip().lower()
        return tipo in {"mesero", "administrador"}

    def puede_asignar_mesa(self, usuario):
        tipo = (getattr(usuario, "tipo_usuario", "") or "").strip().lower()
        return tipo in {"cliente", "mesero", "administrador"}

    def mesa_payload(self, mesa):
        return {
            "id": mesa.get("id"),
            "estado": mesa.get("estado") or "disponible",
            "id_usuario": mesa.get("id_usuario"),
            "cliente_nombre": mesa.get("cliente_nombre") or "",
            "cliente_correo": mesa.get("cliente_correo") or "",
            "asignado_en": mesa.get("asignado_en"),
        }


_mesa_helper = MesaApiHelper()


@csrf_exempt
def api_mesas(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    body = _mesa_helper.leer_json(request)
    usuario, error = _mesa_helper.resolver_usuario(request, body)
    if error:
        return error

    if not _mesa_helper.puede_ver_mesas(usuario):
        return JsonResponse({"error": "Solo meseros o administradores pueden ver las mesas"}, status=403)

    mesas = [_mesa_helper.mesa_payload(mesa) for mesa in _mesa_service.listar()]
    return JsonResponse(mesas, safe=False)


@csrf_exempt
def api_asignar_mesa(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    body = _mesa_helper.leer_json(request)
    usuario, error = _mesa_helper.resolver_usuario(request, body)
    if error:
        return error

    if not _mesa_helper.puede_asignar_mesa(usuario):
        return JsonResponse({"error": "No autorizado para asignar mesa"}, status=403)

    mesa = _mesa_service.asignar_a_usuario(usuario)
    if not mesa:
        return JsonResponse({"error": "No hay mesas disponibles en este momento"}, status=409)

    return JsonResponse(_mesa_helper.mesa_payload(mesa), status=201)


@csrf_exempt
def api_mi_mesa(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    body = _mesa_helper.leer_json(request)
    usuario, error = _mesa_helper.resolver_usuario(request, body)
    if error:
        return error

    mesa = _mesa_service.mesa_por_usuario(usuario.id_usuario)
    if not mesa:
        return JsonResponse({"error": "El usuario no tiene mesa asignada"}, status=404)

    return JsonResponse(_mesa_helper.mesa_payload(mesa))


@csrf_exempt
def api_actualizar_mesa(request, mesa_id):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    body = _mesa_helper.leer_json(request)
    usuario, error = _mesa_helper.resolver_usuario(request, body)
    if error:
        return error

    if not _mesa_helper.puede_ver_mesas(usuario):
        return JsonResponse({"error": "Solo meseros o administradores pueden actualizar mesas"}, status=403)

    mesa = _mesa_service.actualizar_estado(mesa_id, body.get("estado"))
    if not mesa:
        return JsonResponse({"error": "Mesa o estado no valido"}, status=400)

    return JsonResponse(_mesa_helper.mesa_payload(mesa))
