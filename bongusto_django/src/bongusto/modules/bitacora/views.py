"""Vistas del módulo bitácora con una estructura clara y fácil de seguir."""

from collections import defaultdict
from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from bongusto.application.services import BitacoraService, UsuarioService
from bongusto.infrastructure.pdf_generator import crear_pdf_compuesto


# Se crean las instancias de los servicios para reutilizar su lógica en las vistas.
_service = BitacoraService()
_usuario_service = UsuarioService()


class BitacoraPageHelper:
    """Aquí se deja la lógica de apoyo para filtros, agrupación y reportes, así las vistas quedan más limpias."""

    # Lee los filtros que llegan por la URL.
    def leer_filtros(self, request):
        return {
            "usuario": request.GET.get("usuario", ""),
            "accion": request.GET.get("accion", ""),
        }

    # Lista los registros aplicando los filtros actuales.
    def listar_logs(self, filtros):
        try:
            return _service.listar_filtrado(filtros["usuario"], filtros["accion"])
        except Exception:
            return []

    # Busca un registro puntual usando su id.
    def buscar_log(self, pk):
        try:
            return _service.buscar_por_id(pk)
        except Exception:
            return None

    # Lista los usuarios del sistema.
    # Esto sirve como apoyo en formularios o vistas de detalle.
    def listar_usuarios(self):
        try:
            return _usuario_service.listar_todos()
        except Exception:
            return []

    # Agrupa los registros por día para mostrarlos de una forma más organizada.
    # También convierte la fecha en etiquetas como Hoy, Ayer o la fecha completa.
    def agrupar_logs_por_dia(self, logs):
        hoy = timezone.localdate()
        ayer = hoy - timedelta(days=1)
        agrupados = defaultdict(list)

        # Se recorren los logs y se agrupan usando la fecha local.
        for log in logs:
            fecha_local = timezone.localtime(log.fecha_accion) if log.fecha_accion else None
            fecha_clave = fecha_local.date() if fecha_local else None
            agrupados[fecha_clave].append({"registro": log, "fecha_local": fecha_local})

        grupos = []

        # Se ordenan las fechas desde la más reciente hasta la más antigua.
        fechas = sorted(
            agrupados.keys(),
            key=lambda item: item or timezone.datetime.min.date(),
            reverse=True,
        )

        for fecha_clave in fechas:
            if fecha_clave == hoy:
                titulo = "Hoy"
            elif fecha_clave == ayer:
                titulo = "Ayer"
            elif fecha_clave:
                titulo = fecha_clave.strftime("%d de %B de %Y")
            else:
                titulo = "Sin fecha"

            grupos.append(
                {
                    "titulo": titulo,
                    "fecha": fecha_clave.strftime("%d/%m/%Y") if fecha_clave else "-",
                    "registros": agrupados[fecha_clave],
                }
            )

        return grupos

    # Construye toda la información que se va a usar en el reporte PDF.
    # Aquí se organizan los bloques, tablas y resúmenes del reporte.
    def construir_reporte(self, logs):
        logs = list(logs)

        # Diccionarios para resumir la actividad general.
        actividad_por_fecha = defaultdict(int)
        movimientos_por_usuario = defaultdict(int)

        # Listas que luego se convierten en tablas dentro del PDF.
        tabla_principal = []
        acciones_rows = []
        cambios_rows = []

        for log in logs:
            usuario = log.id_usuario.nombre_completo() if log.id_usuario else "Sin usuario"
            accion = log.accion or "-"
            fecha = log.fecha_accion.strftime("%d/%m/%Y %H:%M:%S") if log.fecha_accion else "-"
            fecha_corta = log.fecha_accion.strftime("%Y-%m-%d") if log.fecha_accion else "Sin fecha"

            tabla_principal.append([str(log.id_log), usuario, accion, fecha])
            acciones_rows.append([usuario, accion, fecha])
            cambios_rows.append([usuario, accion])

            # Aquí se van sumando los totales para los resúmenes.
            actividad_por_fecha[fecha_corta] += 1
            movimientos_por_usuario[usuario] += 1

        # Se arman las tablas resumen.
        actividad_rows = [[fecha, str(total)] for fecha, total in sorted(actividad_por_fecha.items(), reverse=True)] or [["Sin fecha", "0"]]
        usuarios_rows = [[usuario, str(total)] for usuario, total in sorted(movimientos_por_usuario.items(), key=lambda item: item[1], reverse=True)] or [["Sin movimientos", "0"]]

        # Se devuelven los bloques finales que necesita el generador de PDF.
        return [
            {
                "heading": "Tabla principal de bitacora",
                "headers": ["ID", "Usuario", "Accion", "Fecha"],
                "rows": tabla_principal or [["-", "-", "-", "-"]],
            },
            {
                "heading": "Acciones realizadas por usuarios",
                "headers": ["Usuario", "Accion", "Fecha"],
                "rows": acciones_rows[:12] or [["Sin usuario", "-", "-"]],
            },
            {
                "heading": "Cambios en el sistema",
                "headers": ["Usuario", "Cambio"],
                "rows": cambios_rows[:12] or [["Sin registros", "-"]],
            },
            {
                "heading": "Actividad por fecha",
                "headers": ["Fecha", "Movimientos"],
                "rows": actividad_rows,
            },
            {
                "heading": "Usuarios con mas movimientos",
                "headers": ["Usuario", "Movimientos"],
                "rows": usuarios_rows,
            },
        ]


# Se crea una instancia del helper para reutilizar toda esta lógica.
_helper = BitacoraPageHelper()


# Vista principal de la bitácora.
# Muestra el listado de registros, los grupos por día y los filtros aplicados.
def index(request):
    filtros = _helper.leer_filtros(request)
    logs = _helper.listar_logs(filtros)
    return render(
        request,
        "bitacora/index.html",
        {
            "logs": logs,
            "grupos_logs": _helper.agrupar_logs_por_dia(logs),
            "filtros": filtros,
        },
    )


# La bitácora no se crea manualmente desde una vista.
# Por eso esta ruta simplemente devuelve al listado.
def create(request):
    return redirect("/bitacora")


# Vista para mostrar el detalle de un registro.
def ver(request, pk):
    bitacora = _helper.buscar_log(pk)
    if not bitacora:
        return redirect("/bitacora")

    return render(
        request,
        "bitacora/form.html",
        {
            "bitacora": bitacora,
            "usuarios": _helper.listar_usuarios(),
            "accion": "Ver",
            "readonly": True,
        },
    )


# La bitácora no se guarda manualmente desde formulario.
def store(request):
    return redirect("/bitacora")


# En realidad no se edita, solo redirige al detalle del registro.
def edit(request, pk):
    return redirect(f"/bitacora/{pk}")


# Tampoco se actualiza desde aquí, solo vuelve al detalle.
def update(request, pk):
    return redirect(f"/bitacora/{pk}")


# No se permite eliminar manualmente desde esta vista.
def delete(request, pk):
    return redirect("/bitacora")


# Genera el reporte PDF de la bitácora usando los filtros actuales.
def reporte(request):
    try:
        filtros = _helper.leer_filtros(request)
        logs = _helper.listar_logs(filtros)

        # Se arma el PDF a partir de los bloques construidos por el helper.
        pdf = crear_pdf_compuesto("Reporte de Bitacora", _helper.construir_reporte(logs))

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="reporte_bitacora.pdf"'
        return response
    except Exception:
        return HttpResponse("No fue posible generar el reporte de bitacora.", status=500)