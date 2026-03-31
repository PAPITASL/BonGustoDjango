"""Vistas del modulo calificaciones en un estilo simple."""

import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from bongusto.application.services import CalificacionService
from bongusto.domain.models import CalificacionCliente
from bongusto.infrastructure.pdf_generator import crear_pdf_compuesto
from bongusto.modules.shared.api_auth import api_login_required, api_owner_or_role


_service = CalificacionService()


class CalificacionPageHelper:
    """Reune conversiones y validaciones del modulo."""

    def leer_filtros(self, request):
        return {
            "usuario": request.GET.get("usuario", ""),
            "puntaje": request.GET.get("puntaje", ""),
        }

    def listar_filtrado(self, filtros):
        try:
            return _service.listar_filtrado(filtros["usuario"], filtros["puntaje"])
        except Exception:
            return []

    def buscar(self, pk):
        try:
            return _service.buscar_por_id(pk)
        except Exception:
            return None

    def leer_json(self, request):
        try:
            return json.loads(request.body or "{}"), None
        except json.JSONDecodeError:
            return None, JsonResponse({"error": "JSON invalido"}, status=400)

    def calificacion_to_dict(self, item):
        return {
            "id_calificacion": item.id_calificacion,
            "id_usuario": item.id_usuario_id,
            "nombre_usuario": item.id_usuario.nombre_completo() if item.id_usuario else "Cliente sin usuario",
            "id_pedido": item.id_pedido_id,
            "calificacion_comida": int(item.calificacion_comida or 0),
            "calificacion_servicio": int(item.calificacion_servicio or 0),
            "calificacion_ambiente": int(item.calificacion_ambiente or 0),
            "promedio": float(item.promedio or 0),
            "observaciones": item.observaciones or "",
            "fecha_calificacion": item.fecha_calificacion.strftime("%d/%m/%Y %H:%M") if item.fecha_calificacion else "",
        }

    def construir_reporte(self, calificaciones):
        filas = []
        for item in calificaciones:
            filas.append([
                str(item.id_calificacion),
                item.id_usuario.nombre_completo() if item.id_usuario else "Sin usuario",
                str(item.id_pedido_id or "-"),
                str(item.calificacion_comida or 0),
                str(item.calificacion_servicio or 0),
                str(item.calificacion_ambiente or 0),
                str(item.promedio),
                item.fecha_calificacion.strftime("%d/%m/%Y %H:%M") if item.fecha_calificacion else "-",
            ])

        return [{
            "heading": "Tabla principal de calificaciones",
            "headers": ["ID", "Cliente", "Pedido", "Comida", "Servicio", "Ambiente", "Promedio", "Fecha"],
            "rows": filas or [["-", "-", "-", "-", "-", "-", "-", "-"]],
        }]

    def validar_estrellas(self, comida, servicio, ambiente):
        for valor in (comida, servicio, ambiente):
            if valor < 1 or valor > 5:
                return False
        return True


_helper = CalificacionPageHelper()


def index(request):
    filtros = _helper.leer_filtros(request)
    calificaciones = _helper.listar_filtrado(filtros)
    return render(request, "calificacion/index.html", {"calificaciones": calificaciones, "filtros": filtros})


def ver(request, pk):
    calificacion = _helper.buscar(pk)
    if not calificacion:
        return redirect("/calificaciones")
    return render(request, "calificacion/form.html", {"calificacion": calificacion})


def reporte(request):
    try:
        filtros = _helper.leer_filtros(request)
        calificaciones = _helper.listar_filtrado(filtros)
        pdf = crear_pdf_compuesto("Reporte de Calificaciones", _helper.construir_reporte(calificaciones))
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="reporte_calificaciones.pdf"'
        return response
    except Exception:
        return HttpResponse("No fue posible generar el reporte de calificaciones.", status=500)


@csrf_exempt
@api_login_required()
def api_crear(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    data, error = _helper.leer_json(request)
    if error:
        return error

    id_usuario = data.get("id_usuario")
    id_pedido = data.get("id_pedido")
    comida = int(data.get("calificacion_comida") or 0)
    servicio = int(data.get("calificacion_servicio") or 0)
    ambiente = int(data.get("calificacion_ambiente") or 0)
    observaciones = (data.get("observaciones") or "").strip()

    if not id_usuario:
        return JsonResponse({"error": "id_usuario es obligatorio"}, status=400)

    if not api_owner_or_role(request, id_usuario, roles={"mesero", "administrador"}):
        return JsonResponse({"error": "No autorizado para registrar esta calificacion"}, status=403)

    if not _helper.validar_estrellas(comida, servicio, ambiente):
        return JsonResponse({"error": "Las calificaciones deben estar entre 1 y 5 estrellas."}, status=400)

    usuario = _service.buscar_usuario_por_id(id_usuario)
    if not usuario:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

    pedido = _service.buscar_pedido_por_id(id_pedido) if id_pedido else None
    calificacion = CalificacionCliente(
        id_usuario=usuario,
        id_pedido=pedido,
        calificacion_comida=comida,
        calificacion_servicio=servicio,
        calificacion_ambiente=ambiente,
        observaciones=observaciones,
    )
    _service.guardar(calificacion)
    return JsonResponse(_helper.calificacion_to_dict(calificacion), status=201)
