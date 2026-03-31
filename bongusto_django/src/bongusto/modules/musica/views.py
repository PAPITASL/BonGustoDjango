"""Vistas del modulo musica en un estilo simple para principiantes."""

from collections import defaultdict
import json
from types import SimpleNamespace

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from bongusto.application.services import MusicaService
from bongusto.domain.models import Musica, Reserva, SolicitudMusica
from bongusto.infrastructure.pdf_generator import crear_pdf_compuesto
from bongusto.modules.shared.api_auth import api_login_required, api_owner_or_role, resolver_usuario_api
from bongusto.modules.shared.audit import registrar_movimiento
from bongusto.modules.shared.excel_import import leer_filas_excel, texto_limpio
from bongusto.modules.shared.table_state import MesaStateService


_service = MusicaService()
_mesa_service = MesaStateService()


class MusicaPageHelper:
    """Deja la logica repetida en un solo lugar."""

    def listar_musicas(self):
        try:
            return _service.listar_todas()
        except Exception:
            return []

    def buscar_musica(self, pk):
        try:
            return _service.buscar_por_id(pk)
        except Exception:
            return None

    def render_index(self, request, mensaje="", error=""):
        return render(request, "musica/index.html", {"musicas": self.listar_musicas(), "mensaje": mensaje, "error": error})

    def render_form(self, request, musica, accion, readonly=False, error=""):
        return render(
            request,
            "musica/create.html",
            {
                "musica": musica,
                "readonly": readonly,
                "accion": accion,
                "error": error,
            },
        )

    def cargar_desde_post(self, request, musica):
        musica.nombre_musica = (request.POST.get("nombre_musica", "") or "").strip()
        musica.artista_musica = (request.POST.get("artista_musica", "") or "").strip()
        duracion = (request.POST.get("duracion_musica", "") or "").strip()
        musica.duracion_musica = duracion or None
        return musica

    def validar(self, request, musica, accion):
        if not musica.nombre_musica:
            return None, self.render_form(request, musica, accion, error="Debes escribir el nombre de la cancion.")

        if not musica.artista_musica:
            return None, self.render_form(request, musica, accion, error="Debes escribir el artista.")

        return musica, None

    def guardar(self, musica):
        _service.guardar(musica)

    def eliminar(self, pk):
        _service.eliminar(pk)

    def construir_mensaje_importacion(self, creados, repetidos):
        if not creados and not repetidos:
            return ""
        return f"Importacion completada. Nuevas: {creados or 0}. Repetidas detectadas: {repetidos or 0}."

    def construir_reporte(self, musicas):
        musicas = list(musicas)
        musica_ids = [musica.id_musica for musica in musicas]
        solicitudes = list(SolicitudMusica.objects.select_related("id_usuario", "id_musica").filter(id_musica_id__in=musica_ids))

        solicitudes_por_musica = defaultdict(int)
        solicitudes_por_usuario = defaultdict(int)
        solicitudes_por_artista = defaultdict(int)
        solicitudes_por_reserva = defaultdict(int)

        for solicitud in solicitudes:
            self._sumar_solicitud(
                solicitud,
                solicitudes_por_musica,
                solicitudes_por_usuario,
                solicitudes_por_artista,
                solicitudes_por_reserva,
            )

        horas_pico = self._horas_pico(solicitudes_por_reserva)
        tabla_principal = []
        canciones_rows = []

        for musica in musicas:
            total = solicitudes_por_musica.get(musica.id_musica, 0)
            artista = musica.artista_musica or "Sin artista"

            tabla_principal.append([
                str(musica.id_musica),
                musica.nombre_musica or "-",
                artista,
                str(musica.duracion_musica or "-"),
                str(total),
            ])

            canciones_rows.append([
                musica.nombre_musica or f"Cancion {musica.id_musica}",
                artista,
                str(total),
            ])

        canciones_rows.sort(key=lambda row: (int(row[2]), row[0]), reverse=True)

        return [
            {
                "heading": "Tabla canciones y actividad musical",
                "headers": ["ID", "Cancion", "Artista", "Duracion", "Solicitudes"],
                "rows": tabla_principal or [["-", "Sin canciones", "-", "-", "0"]],
                "col_widths": [1.2 * 72 / 2.54, 5.4 * 72 / 2.54, 4.8 * 72 / 2.54, 2.4 * 72 / 2.54, 2.7 * 72 / 2.54],
            },
            {
                "heading": "Canciones mas solicitadas",
                "headers": ["Cancion", "Artista", "Solicitudes"],
                "rows": canciones_rows[:10] or [["Sin canciones", "-", "0"]],
            },
            {
                "heading": "Artistas con mas solicitudes",
                "headers": ["Artista", "Solicitudes"],
                "rows": self._rows_ordenadas(solicitudes_por_artista, "Sin artista"),
            },
            {
                "heading": "Usuarios que mas usan la rocola",
                "headers": ["Usuario", "Solicitudes"],
                "rows": self._rows_ordenadas(solicitudes_por_usuario, "Sin uso registrado"),
            },
            {
                "heading": "Horas pico de uso musical",
                "paragraph": "Calculado con la hora de la reserva asociada a cada solicitud musical.",
                "headers": ["Hora", "Solicitudes"],
                "rows": self._rows_ordenadas(horas_pico, "Sin hora registrada"),
            },
        ]

    def _sumar_solicitud(self, solicitud, solicitudes_por_musica, solicitudes_por_usuario, solicitudes_por_artista, solicitudes_por_reserva):
        if solicitud.id_musica_id:
            solicitudes_por_musica[solicitud.id_musica_id] += 1
            artista = "Sin artista"
            if solicitud.id_musica and solicitud.id_musica.artista_musica:
                artista = solicitud.id_musica.artista_musica
            solicitudes_por_artista[artista] += 1

        if solicitud.id_usuario_id:
            nombre_usuario = f"Usuario {solicitud.id_usuario_id}"
            if solicitud.id_usuario:
                nombre_usuario = solicitud.id_usuario.nombre_completo() or nombre_usuario
            solicitudes_por_usuario[nombre_usuario] += 1

        if solicitud.id_res is not None:
            solicitudes_por_reserva[int(solicitud.id_res)] += 1

    def _horas_pico(self, solicitudes_por_reserva):
        reservas = {
            int(reserva.id_res): reserva
            for reserva in Reserva.objects.filter(id_res__in=list(solicitudes_por_reserva.keys())).only("id_res", "hora_reser")
            if reserva.id_res is not None
        }

        horas_pico = defaultdict(int)
        for id_res, total in solicitudes_por_reserva.items():
            reserva = reservas.get(id_res)
            hora = reserva.hora_reser if reserva and reserva.hora_reser else "Sin hora"
            horas_pico[hora] += total
        return horas_pico

    def _rows_ordenadas(self, datos, etiqueta_vacia):
        rows = [[clave, str(total)] for clave, total in sorted(datos.items(), key=lambda item: item[1], reverse=True)]
        return rows[:10] or [[etiqueta_vacia, "0"]]

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


_helper = MusicaPageHelper()


def _usuario_local_musica():
    if not settings.DEBUG:
        return None
    return SimpleNamespace(id_usuario=0, tipo_usuario="mesero", estado="Activo")


def _resolver_usuario_musica(request):
    usuario, _, error_response = resolver_usuario_api(request)
    if usuario:
        return usuario, None

    usuario_dev = _usuario_local_musica()
    if usuario_dev:
        return usuario_dev, None

    return None, error_response


def index(request):
    mensaje = _helper.construir_mensaje_importacion(request.GET.get("creados", ""), request.GET.get("repetidos", ""))
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

    try:
        _helper.guardar(musica)
        registrar_movimiento(request, f"Creacion de cancion {musica.nombre_musica or musica.id_musica} de {musica.artista_musica or 'artista no definido'}.")
        return redirect("/musicas")
    except Exception as exc:
        return _helper.render_form(request, musica, "Agregar", error=str(exc))


def eliminar(request, pk):
    try:
        musica = _helper.buscar_musica(pk)
        _helper.eliminar(pk)
        if musica:
            registrar_movimiento(request, f"Eliminacion de cancion {musica.nombre_musica or musica.id_musica}.")
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

                musica_existente = Musica.objects.filter(nombre_musica__iexact=nombre, artista_musica__iexact=artista).first()
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
        return redirect(f"/musicas?creados={nuevos}&repetidos={total_repetidos}")
    except Exception as exc:
        return _helper.render_index(request, error=str(exc))


def reporte(request):
    try:
        musicas = _helper.listar_musicas()
        data = crear_pdf_compuesto("Reporte de Musica", _helper.construir_reporte(musicas))
        response = HttpResponse(data, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="reporte_musica.pdf"'
        return response
    except Exception:
        return HttpResponse("No fue posible generar el reporte de musica.", status=500)


def api_listar(request):
    musicas = _helper.listar_musicas().order_by("nombre_musica", "artista_musica")
    return JsonResponse([_helper.musica_to_dict(musica) for musica in musicas], safe=False)


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
    id_res = data.get("id_res")
    nombre_musica = (data.get("nombre_musica") or "").strip()
    artista_musica = (data.get("artista_musica") or "").strip()

    if not id_usuario:
        return JsonResponse({"error": "id_usuario es obligatorio"}, status=400)

    if not api_owner_or_role(request, id_usuario, roles={"mesero", "administrador"}):
        return JsonResponse({"error": "No autorizado para registrar esta solicitud"}, status=403)

    usuario = _service.buscar_usuario_por_id(id_usuario)
    musica = _helper.buscar_musica(id_musica) if id_musica else None

    if not musica:
        if not nombre_musica or not artista_musica:
            return JsonResponse({"error": "Debes enviar una cancion existente o escribir nombre y artista."}, status=400)

        musica = Musica.objects.filter(nombre_musica__iexact=nombre_musica, artista_musica__iexact=artista_musica).first()
        if not musica:
            musica = Musica(nombre_musica=nombre_musica, artista_musica=artista_musica)
            musica.save()

    if not usuario:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

    solicitud = SolicitudMusica(id_usuario=usuario, id_musica=musica, id_res=id_res, estado_solicitud="pendiente")
    solicitud.save()

    return JsonResponse(
        {
            "id_solicitud": solicitud.id_solicitud,
            "estado_solicitud": solicitud.estado_solicitud,
            "musica": _helper.musica_to_dict(musica),
        },
        status=201,
    )


def api_cola(request):
    usuario, error_response = _resolver_usuario_musica(request)
    if error_response:
        return error_response

    request.api_user = usuario
    solicitudes = SolicitudMusica.objects.select_related("id_usuario", "id_musica").order_by("id_solicitud")
    data = []

    for item in solicitudes:
        musica = item.id_musica
        mesa = _mesa_service.mesa_por_usuario(item.id_usuario_id) or {}
        mesa_id = mesa.get("id")
        data.append(
            {
                "id_solicitud": item.id_solicitud,
                "estado_solicitud": item.estado_solicitud or "",
                "id_usuario": item.id_usuario_id,
                "cliente_nombre": item.id_usuario.nombre_completo() if item.id_usuario else "",
                "mesa_id": mesa_id,
                "mesa_label": f"Mesa {mesa_id}" if mesa_id else "",
                "id_res": item.id_res,
                "musica": _helper.musica_to_dict(musica) if musica else {
                    "id_musica": None,
                    "nombre_musica": "",
                    "artista_musica": "",
                    "duracion_musica": "",
                },
            }
        )

    return JsonResponse(data, safe=False)
