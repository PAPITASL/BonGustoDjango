"""Vistas del módulo calificaciones con una estructura sencilla y clara."""

import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from bongusto.application.services import CalificacionService
from bongusto.domain.models import CalificacionCliente
from bongusto.infrastructure.pdf_generator import crear_pdf_compuesto
from bongusto.modules.shared.api_auth import api_login_required, api_owner_or_role


# Se crea la instancia del servicio para usar toda la lógica del módulo
_service = CalificacionService()


class CalificacionPageHelper:
    """Aquí se deja la lógica de apoyo (filtros, validaciones, conversiones) para no cargar tanto las vistas."""

    # Lee los filtros que vienen por la URL
    def leer_filtros(self, request):
        return {
            "usuario": request.GET.get("usuario", ""),
            "puntaje": request.GET.get("puntaje", ""),
        }

    # Lista las calificaciones usando los filtros actuales
    def listar_filtrado(self, filtros):
        try:
            return _service.listar_filtrado(filtros["usuario"], filtros["puntaje"])
        except Exception:
            return []

    # Busca una calificación por id
    def buscar(self, pk):
        try:
            return _service.buscar_por_id(pk)
        except Exception:
            return None

    # Intenta leer el body como JSON
    # Si viene mal, devuelve error directamente
    def leer_json(self, request):
        try:
            return json.loads(request.body or "{}"), None
        except json.JSONDecodeError:
            return None, JsonResponse({"error": "JSON invalido"}, status=400)

    # Convierte una calificación a diccionario (para respuestas tipo API)
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

    # Convierte un pedido a diccionario simple para la app.
    def pedido_to_dict(self, pedido):
        if not pedido:
            return None
        mesa = getattr(pedido, "mesa", None)
        mesa_label = ""
        if mesa:
            mesa_label = getattr(mesa, "etiqueta", "") or f"Mesa {getattr(mesa, 'numero_mesa', '')}"
        return {
            "id_pedido": pedido.id_pedido,
            "id_usuario": pedido.id_usuario_id,
            "mesa_id": getattr(pedido, "mesa_id", None),
            "mesa_label": mesa_label or "Sin mesa",
            "estado": getattr(pedido, "estado_pedido", "abierto"),
            "total_pedido": float(pedido.total_pedido or 0),
            "fecha_pedido": pedido.fecha_pedido.isoformat() if pedido.fecha_pedido else "",
            "fecha_finalizacion": (
                pedido.fecha_finalizacion.isoformat() if getattr(pedido, "fecha_finalizacion", None) else ""
            ),
        }

    # Construye la info que se usa en el PDF
    # Básicamente arma la tabla principal
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

    # Valida que las estrellas estén entre 1 y 5
    def validar_estrellas(self, comida, servicio, ambiente):
        for valor in (comida, servicio, ambiente):
            if valor < 1 or valor > 5:
                return False
        return True


# Instancia del helper para reutilizar esta lógica
_helper = CalificacionPageHelper()


# Vista principal
# Muestra el listado con filtros
def index(request):
    filtros = _helper.leer_filtros(request)
    calificaciones = _helper.listar_filtrado(filtros)
    return render(request, "calificacion/index.html", {"calificaciones": calificaciones, "filtros": filtros})


# Vista de detalle
def ver(request, pk):
    calificacion = _helper.buscar(pk)

    # Si no existe, vuelve al listado
    if not calificacion:
        return redirect("/calificaciones")

    return render(request, "calificacion/form.html", {"calificacion": calificacion})


# Genera el PDF de calificaciones
def reporte(request):
    try:
        filtros = _helper.leer_filtros(request)
        calificaciones = _helper.listar_filtrado(filtros)

        # Se construye el PDF con la info del helper
        pdf = crear_pdf_compuesto("Reporte de Calificaciones", _helper.construir_reporte(calificaciones))

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="reporte_calificaciones.pdf"'
        return response
    except Exception:
        return HttpResponse("No fue posible generar el reporte de calificaciones.", status=500)


# API para crear una calificación
# csrf_exempt porque puede venir desde app móvil o frontend externo
@csrf_exempt
@api_login_required()
def api_crear(request):

    # Solo acepta POST
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    # Lee el JSON enviado
    data, error = _helper.leer_json(request)
    if error:
        return error

    # Datos principales
    id_usuario = data.get("id_usuario")
    id_pedido = data.get("id_pedido")
    comida = int(data.get("calificacion_comida") or 0)
    servicio = int(data.get("calificacion_servicio") or 0)
    ambiente = int(data.get("calificacion_ambiente") or 0)
    observaciones = (data.get("observaciones") or "").strip()

    # Usuario obligatorio
    if not id_usuario:
        return JsonResponse({"error": "id_usuario es obligatorio"}, status=400)

    # Validación de permisos
    if not api_owner_or_role(request, id_usuario, roles={"mesero", "administrador"}):
        return JsonResponse({"error": "No autorizado para registrar esta calificacion"}, status=403)

    # Validación de rango de estrellas
    if not _helper.validar_estrellas(comida, servicio, ambiente):
        return JsonResponse({"error": "Las calificaciones deben estar entre 1 y 5 estrellas."}, status=400)

    # Busca usuario real
    usuario = _service.buscar_usuario_por_id(id_usuario)
    if not usuario:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

    # La calificacion debe amarrarse a un pedido concreto.
    if not id_pedido:
        return JsonResponse({"error": "id_pedido es obligatorio para calificar"}, status=400)

    pedido = _service.buscar_pedido_por_id(id_pedido)
    if not pedido:
        return JsonResponse({"error": "No existe el pedido indicado para calificar"}, status=404)
    if getattr(pedido, "id_usuario_id", None) and int(pedido.id_usuario_id) != int(id_usuario):
        return JsonResponse({"error": "El pedido no pertenece al cliente autenticado"}, status=403)
    if getattr(pedido, "estado_pedido", "abierto") not in _service.ESTADOS_CALIFICABLES:
        return JsonResponse({"error": "Solo se puede calificar un pedido finalizado"}, status=400)
    if _service.pedido_ya_calificado(pedido.id_pedido):
        return JsonResponse({"error": "Este pedido ya fue calificado."}, status=400)

    # Se crea la calificación
    calificacion = CalificacionCliente(
        id_usuario=usuario,
        id_pedido=pedido,
        calificacion_comida=comida,
        calificacion_servicio=servicio,
        calificacion_ambiente=ambiente,
        observaciones=observaciones,
    )

    # Se guarda
    try:
        _service.guardar(calificacion)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    # Respuesta JSON
    return JsonResponse(_helper.calificacion_to_dict(calificacion), status=201)


@csrf_exempt
@api_login_required()
def api_pendiente(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    id_usuario = request.GET.get("id_usuario")
    if not id_usuario:
        return JsonResponse({"error": "id_usuario es obligatorio"}, status=400)

    if not api_owner_or_role(request, id_usuario, roles={"mesero", "administrador"}):
        return JsonResponse({"error": "No autorizado para consultar calificaciones pendientes"}, status=403)

    pedido = _service.buscar_pedido_pendiente_calificacion_por_usuario(id_usuario)
    if not pedido:
        return JsonResponse({"error": "No existe un pedido finalizado pendiente de calificacion"}, status=404)

    if _service.pedido_ya_calificado(pedido.id_pedido):
        return JsonResponse({"error": "Este pedido ya fue calificado."}, status=409)

    return JsonResponse(_helper.pedido_to_dict(pedido))
