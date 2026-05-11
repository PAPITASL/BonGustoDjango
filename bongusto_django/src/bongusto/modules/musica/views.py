"""Vistas del modulo musica con cola en tiempo real e historial."""

from collections import defaultdict
import json
from types import SimpleNamespace

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from bongusto.domain.models import Musica, SolicitudMusica, Usuario
from bongusto.infrastructure.pdf_generator import crear_pdf_compuesto
from bongusto.modules.musica.services import MusicaService
from bongusto.modules.shared.api_auth import api_login_required, api_owner_or_role, resolver_usuario_api
from bongusto.modules.shared.audit import registrar_movimiento
from bongusto.modules.shared.excel_import import leer_filas_excel, texto_limpio


_service = MusicaService()


class MusicaPageHelper:
    def listar_musicas(self):
        return _service.listar_todas()

    def buscar_musica(self, pk):
        return _service.buscar_por_id(pk)

    def render_index(self, request, mensaje="", error=""):
        snapshot = _service.snapshot()
        return render(
            request,
            "musica/index.html",
            {
                "musicas": self.listar_musicas(),
                "mensaje": mensaje,
                "error": error,
                "cola_activa": snapshot.get("cola", []),
                "cancion_actual": snapshot.get("actual"),
                "total_activas": snapshot.get("total_activas", 0),
                "historial_reciente": [
                    item for item in _service.historial() if item.get("estado_solicitud") != "eliminada"
                ][:40],
            },
        )

    def render_form(self, request, musica, accion, readonly=False, error=""):
        return render(
            request,
            "musica/create.html",
            {
                "musica": musica,
                "readonly": readonly,
                "accion": accion,
                "error": error,
                "musicas_catalogo": [self.musica_to_dict(item) for item in self.listar_musicas()],
            },
        )

    def cargar_desde_post(self, request, musica):
        musica.nombre_musica = (request.POST.get("nombre_musica", "") or "").strip()
        musica.artista_musica = (request.POST.get("artista_musica", "") or "").strip()
        duracion = (request.POST.get("duracion_musica", "") or "").strip()
        musica.duracion_musica = self.normalizar_duracion(duracion)
        return musica

    def normalizar_duracion(self, valor):
        valor = (valor or "").strip()
        if not valor:
            return None
        valor = valor.replace(",", ".")
        if ":" in valor:
            partes = [parte.strip() for parte in valor.split(":", 1)]
            if len(partes) == 2 and partes[0].isdigit() and partes[1].isdigit():
                minutos = int(partes[0])
                segundos = int(partes[1])
                total = minutos + (segundos / 60)
                return round(total, 2)
        try:
            return round(float(valor), 2)
        except (TypeError, ValueError):
            return None

    def validar(self, request, musica, accion):
        if not musica.nombre_musica:
            return None, self.render_form(request, musica, accion, error="Debes escribir el nombre de la cancion.")
        if not musica.artista_musica:
            return None, self.render_form(request, musica, accion, error="Debes escribir el artista.")
        return musica, None

    def guardar(self, musica):
        return _service.guardar(musica)

    def eliminar(self, pk):
        return _service.eliminar(pk)

    def construir_reporte(self, fecha=None, periodo=None):
        resumen = _service.resumen_pdf(fecha=fecha, periodo=periodo)
        historial = resumen["historial"]

        tabla_historial = [
            [
                str(item["id_solicitud"]),
                item["cancion"] or "-",
                item["artista"] or "-",
                item["cliente_nombre"] or "-",
                item["mesa_label"] or "-",
                item["estado_solicitud"] or "-",
                item["fecha_solicitud"] or "-",
                item["fecha_inicio_reproduccion"] or "-",
                item["fecha_finalizacion"] or "-",
            ]
            for item in historial[:80]
        ] or [["-", "-", "-", "-", "-", "-", "-", "-", "-"]]

        ranking = [
            [item["cancion"] or "-", item["artista"] or "-", str(item["total"])]
            for item in resumen["ranking"]
        ] or [["Sin datos", "-", "0"]]

        eliminadas = [
            [
                item["cancion"] or "-",
                item["artista"] or "-",
                item["cliente_nombre"] or "-",
                item["mesa_label"] or "-",
                item["eliminado_por"] or "-",
                item["motivo_eliminacion"] or "-",
            ]
            for item in historial
            if item["estado_solicitud"] == "eliminada"
        ] or [["Sin eliminaciones", "-", "-", "-", "-", "-"]]

        horas = defaultdict(int)
        por_dia = defaultdict(int)
        for item in historial:
            fecha_solicitud = item.get("fecha_solicitud") or ""
            if "T" in fecha_solicitud:
                fecha, hora = fecha_solicitud.split("T", 1)
                por_dia[fecha] += 1
                horas[hora[:2] + ":00"] += 1

        return [
            {
                "heading": "Historial musical completo",
                "headers": ["ID", "Cancion", "Artista", "Cliente", "Mesa", "Estado", "Solicitud", "Inicio", "Finalizacion"],
                "rows": tabla_historial,
            },
            {
                "heading": "Ranking de canciones mas solicitadas",
                "headers": ["Cancion", "Artista", "Total"],
                "rows": ranking,
            },
            {
                "heading": "Canciones eliminadas por administrador",
                "headers": ["Cancion", "Artista", "Cliente", "Mesa", "Eliminado por", "Motivo"],
                "rows": eliminadas,
            },
            {
                "heading": "Totales por dia",
                "headers": ["Dia", "Total"],
                "rows": [[dia, str(total)] for dia, total in sorted(por_dia.items())] or [["Sin datos", "0"]],
            },
            {
                "heading": "Horas con mas actividad",
                "headers": ["Hora", "Total"],
                "rows": [[hora, str(total)] for hora, total in sorted(horas.items(), key=lambda item: item[1], reverse=True)[:10]] or [["Sin datos", "0"]],
            },
        ]

    def musica_to_dict(self, musica):
        return {
            "id_musica": musica.id_musica,
            "nombre_musica": musica.nombre_musica or "",
            "artista_musica": musica.artista_musica or "",
            "duracion_musica": str(musica.duracion_musica or ""),
        }

    def leer_json(self, request):
        try:
            return json.loads(request.body or "{}"), None
        except json.JSONDecodeError:
            return None, JsonResponse({"error": "JSON invalido"}, status=400)

    def buscar_duplicada(self, nombre, artista):
        nombre_limpio = (nombre or "").strip()
        artista_limpio = (artista or "").strip()
        if not nombre_limpio or not artista_limpio:
            return None
        return Musica.objects.filter(
            nombre_musica__iexact=nombre_limpio,
            artista_musica__iexact=artista_limpio,
        ).first()


_helper = MusicaPageHelper()


def _usuario_local_musica():
    if not settings.DEBUG:
        return None
    return SimpleNamespace(id_usuario=0, tipo_usuario="mesero", estado="Activo")


def _resolver_usuario_musica(request):
    usuario, _, error_response = resolver_usuario_api(request)
    if usuario:
        return usuario, None

    usuario_id = request.session.get("usuario_id")
    if usuario_id:
        usuario = Usuario.objects.filter(pk=usuario_id, estado__iexact="activo").first()
        if usuario:
            return usuario, None

    usuario_dev = _usuario_local_musica()
    if usuario_dev:
        return usuario_dev, None
    return None, error_response


def _es_admin(usuario):
    return (getattr(usuario, "tipo_usuario", "") or "").strip().lower() == "administrador"


def _es_mesero(usuario):
    return (getattr(usuario, "tipo_usuario", "") or "").strip().lower() == "mesero"


def index(request):
    mensaje = request.GET.get("mensaje", "")
    return _helper.render_index(request, mensaje=mensaje)


def nueva(request):
    return _helper.render_form(request, Musica(), "Agregar")


def ver(request, pk):
    musica = _helper.buscar_musica(pk)
    if not musica:
        return redirect("/musicas")
    return _helper.render_form(request, musica, "Ver", readonly=True)


def store(request):
    if request.method != "POST":
        return redirect("/musicas")
    musica = _helper.cargar_desde_post(request, Musica())
    musica, error = _helper.validar(request, musica, "Agregar")
    if error:
        return error
    usuario, error_response = _resolver_usuario_musica(request)
    if error_response:
        return error_response
    try:
        forzar_cola = str(request.POST.get("forzar_cola_duplicada") or "").strip() in {"1", "true", "si", "yes", "on"}
        duplicada = _helper.buscar_duplicada(musica.nombre_musica, musica.artista_musica)
        musica_en_uso = duplicada or musica

        if not duplicada:
            _helper.guardar(musica_en_uso)
        elif not forzar_cola:
            return _helper.render_form(
                request,
                musica,
                "Agregar",
                error="Cancion duplicada. La cancion ya fue registrada previamente.",
            )

        _service.solicitar(
            usuario=usuario,
            musica=musica_en_uso,
            cancion=musica_en_uso.nombre_musica or "",
            artista=musica_en_uso.artista_musica or "",
            duracion_segundos=_helper.normalizar_duracion(str(musica.duracion_musica or "")) or None,
        )
        if duplicada:
            registrar_movimiento(
                request,
                f"Reuso de cancion duplicada {musica_en_uso.nombre_musica or musica_en_uso.id_musica} y agregado a la cola.",
            )
            return redirect(
                f"/musicas?mensaje=Cancion duplicada detectada. Se agrego a la cola sin duplicar el catalogo: {musica_en_uso.nombre_musica}."
            )

        registrar_movimiento(
            request,
            f"Creacion de cancion {musica_en_uso.nombre_musica or musica_en_uso.id_musica} y agregado a la cola.",
        )
        return redirect(f"/musicas?mensaje=Cancion guardada correctamente: {musica_en_uso.nombre_musica}.")
    except Exception as exc:
        return _helper.render_form(request, musica, "Agregar", error=str(exc))


def eliminar(request, pk):
    try:
        musica = _helper.buscar_musica(pk)
        _helper.eliminar(pk)
        if musica:
            registrar_movimiento(request, f"Eliminacion de cancion de catalogo {musica.nombre_musica or musica.id_musica}.")
    except Exception:
        pass
    return redirect("/musicas")


def importar_excel(request):
    if request.method != "POST":
        return redirect("/musicas")

    try:
        filas = leer_filas_excel(request.FILES.get("archivo_excel"))
        total_importados = 0
        total_repetidos = 0
        errores = []

        with transaction.atomic():
            for indice, fila in enumerate(filas, start=2):
                nombre = texto_limpio(fila.get("nombre_musica") or fila.get("cancion") or fila.get("titulo") or fila.get("nombre"))
                artista = texto_limpio(fila.get("artista_musica") or fila.get("artista"))
                duracion = texto_limpio(fila.get("duracion_musica") or fila.get("duracion"))
                if not nombre:
                    errores.append(f"Fila {indice}: falta el nombre de la cancion.")
                    continue
                if not artista:
                    errores.append(f"Fila {indice}: falta el artista.")
                    continue
                musica_existente = Musica.objects.filter(
                    nombre_musica__iexact=nombre,
                    artista_musica__iexact=artista,
                ).first()
                if musica_existente:
                    total_repetidos += 1
                musica = musica_existente or Musica()
                musica.nombre_musica = nombre
                musica.artista_musica = artista
                musica.duracion_musica = duracion or None
                _helper.guardar(musica)
                total_importados += 1

        if total_importados == 0:
            detalle = f" Detalle: {errores[0]}" if errores else ""
            raise ValueError("No se importo ninguna cancion. Revisa encabezados y filas del archivo." + detalle)

        registrar_movimiento(request, f"Importacion masiva de {total_importados} canciones desde archivo Excel.")
        nuevos = total_importados - total_repetidos
        return redirect(f"/musicas?mensaje=Importacion completada. Nuevas: {nuevos}. Repetidas detectadas: {total_repetidos}.")
    except Exception as exc:
        return _helper.render_index(request, error=str(exc))


def reporte(request):
    try:
        fecha = request.GET.get("fecha")
        periodo = request.GET.get("periodo")
        data = crear_pdf_compuesto("Reporte de Historial Musical", _helper.construir_reporte(fecha=fecha, periodo=periodo))
        response = HttpResponse(data, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="reporte_historial_musical.pdf"'
        return response
    except Exception:
        return HttpResponse("No fue posible generar el reporte de musica.", status=500)


def api_listar(request):
    musicas = _helper.listar_musicas()
    return JsonResponse([_helper.musica_to_dict(musica) for musica in musicas], safe=False)


@csrf_exempt
def api_validar_duplicada(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, error_response = _resolver_usuario_musica(request)
    if error_response:
        return error_response
    if not _es_admin(usuario):
        return JsonResponse({"error": "Solo el administrador puede validar duplicados"}, status=403)

    data, error = _helper.leer_json(request)
    if error:
        return error

    nombre = (data.get("nombre_musica") or data.get("cancion") or "").strip()
    artista = (data.get("artista_musica") or data.get("artista") or "").strip()
    if not nombre or not artista:
        return JsonResponse({"duplicate": False, "error": "Debes enviar nombre y artista"}, status=400)

    duplicada = _helper.buscar_duplicada(nombre, artista)
    if not duplicada:
        return JsonResponse({"duplicate": False})

    return JsonResponse(
        {
            "duplicate": True,
            "existing": _helper.musica_to_dict(duplicada),
            "message": "La cancion ya fue registrada previamente.",
        }
    )


@csrf_exempt
@api_login_required()
def api_solicitar(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)
    data, error = _helper.leer_json(request)
    if error:
        return error

    id_usuario = data.get("id_usuario")
    id_musica = data.get("id_musica")
    nombre_musica = (data.get("nombre_musica") or data.get("cancion") or "").strip()
    artista_musica = (data.get("artista_musica") or data.get("artista") or "").strip()
    mesa_id = data.get("mesa_id")
    if not id_usuario:
        return JsonResponse({"error": "id_usuario es obligatorio"}, status=400)
    if not api_owner_or_role(request, id_usuario, roles={"mesero", "administrador"}):
        return JsonResponse({"error": "No autorizado para registrar esta solicitud"}, status=403)

    usuario = _service.buscar_usuario_por_id(id_usuario)
    musica = _helper.buscar_musica(id_musica) if id_musica else None
    if not musica and (not nombre_musica or not artista_musica):
        return JsonResponse({"error": "Debes enviar una cancion existente o escribir nombre y artista."}, status=400)
    if not musica:
        musica = Musica.objects.filter(
            nombre_musica__iexact=nombre_musica,
            artista_musica__iexact=artista_musica,
        ).first()
        if not musica:
            musica = Musica(nombre_musica=nombre_musica, artista_musica=artista_musica)
            musica.save()
    if not usuario:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

    try:
        solicitud = _service.solicitar(
            usuario=usuario,
            musica=musica,
            cancion=nombre_musica,
            artista=artista_musica,
            mesa_id=mesa_id,
            duracion_segundos=data.get("duracion_segundos"),
        )
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse(_service.solicitud_to_dict(solicitud), status=201)


def api_cola(request):
    usuario, error_response = _resolver_usuario_musica(request)
    if error_response:
        return error_response
    mesa_id = request.GET.get("mesa_id")
    return JsonResponse(_service.cola_activa(usuario=usuario, mesa_id=mesa_id), safe=False)


def api_historial(request):
    usuario, error_response = _resolver_usuario_musica(request)
    if error_response:
        return error_response
    if not _es_admin(usuario):
        return JsonResponse({"error": "Solo el administrador puede consultar historial musical"}, status=403)
    data = _service.historial(
        fecha=request.GET.get("fecha"),
        periodo=request.GET.get("periodo"),
        mesa_id=request.GET.get("mesa_id"),
        usuario_id=request.GET.get("usuario_id"),
        estado=request.GET.get("estado"),
        cancion=request.GET.get("cancion"),
    )
    if not request.GET.get("estado"):
        data = [item for item in data if item.get("estado_solicitud") != "eliminada"]
    return JsonResponse(data, safe=False)


@csrf_exempt
def api_eliminar_solicitud(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)
    usuario, error_response = _resolver_usuario_musica(request)
    if error_response:
        return error_response
    if not _es_admin(usuario):
        return JsonResponse({"error": "Solo el administrador puede eliminar canciones"}, status=403)
    payload, _ = _helper.leer_json(request)
    motivo = ""
    if isinstance(payload, dict):
        motivo = (payload.get("motivo") or "").strip()
    if not motivo:
        motivo = (request.POST.get("motivo") or "Eliminada por administrador").strip()
    solicitud = _service.eliminar_solicitud(pk, admin=usuario, motivo=motivo)
    if not solicitud:
        return JsonResponse({"error": "Solicitud musical no encontrada"}, status=404)
    registrar_movimiento(request, f"Eliminacion logica de solicitud musical {pk}.")
    return JsonResponse(_service.solicitud_to_dict(solicitud))


@csrf_exempt
def api_subir(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)
    usuario, error_response = _resolver_usuario_musica(request)
    if error_response:
        return error_response
    if not _es_admin(usuario):
        return JsonResponse({"error": "Solo el administrador puede ordenar la cola"}, status=403)
    solicitud = _service.mover(pk, "up")
    if not solicitud:
        return JsonResponse({"error": "No se pudo mover la cancion"}, status=404)
    return JsonResponse(_service.snapshot())


@csrf_exempt
def api_bajar(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)
    usuario, error_response = _resolver_usuario_musica(request)
    if error_response:
        return error_response
    if not _es_admin(usuario):
        return JsonResponse({"error": "Solo el administrador puede ordenar la cola"}, status=403)
    solicitud = _service.mover(pk, "down")
    if not solicitud:
        return JsonResponse({"error": "No se pudo mover la cancion"}, status=404)
    return JsonResponse(_service.snapshot())


@csrf_exempt
def api_saltar(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)
    usuario, error_response = _resolver_usuario_musica(request)
    if error_response:
        return error_response
    if not _es_admin(usuario):
        return JsonResponse({"error": "Solo el administrador puede saltar canciones"}, status=403)
    solicitud = _service.saltar(pk, admin=usuario)
    if not solicitud:
        return JsonResponse({"error": "Solicitud musical no encontrada"}, status=404)
    registrar_movimiento(request, f"Salto manual de solicitud musical {pk}.")
    return JsonResponse(_service.snapshot())


@csrf_exempt
def api_marcar_reproducida(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)
    usuario, error_response = _resolver_usuario_musica(request)
    if error_response:
        return error_response
    if not _es_admin(usuario):
        return JsonResponse({"error": "Solo el administrador puede cerrar canciones"}, status=403)
    solicitud = _service.marcar_reproducida(pk, admin=usuario)
    if not solicitud:
        return JsonResponse({"error": "Solicitud musical no encontrada"}, status=404)
    registrar_movimiento(request, f"Solicitud musical {pk} marcada como reproducida.")
    return JsonResponse(_service.snapshot())


def api_snapshot(request):
    usuario, error_response = _resolver_usuario_musica(request)
    if error_response:
        return error_response
    snapshot = _service.snapshot()
    snapshot["rol"] = (getattr(usuario, "tipo_usuario", "") or "").strip().lower()
    snapshot["usuario_id"] = getattr(usuario, "id_usuario", None)
    return JsonResponse(snapshot)


__all__ = [
    "index",
    "nueva",
    "ver",
    "store",
    "eliminar",
    "importar_excel",
    "reporte",
    "api_listar",
    "api_validar_duplicada",
    "api_solicitar",
    "api_cola",
    "api_historial",
    "api_eliminar_solicitud",
    "api_subir",
    "api_bajar",
    "api_saltar",
    "api_marcar_reproducida",
    "api_snapshot",
]
