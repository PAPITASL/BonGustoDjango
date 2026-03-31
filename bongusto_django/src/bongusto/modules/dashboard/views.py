"""Vistas sencillas del dashboard."""

from django.http import HttpResponse
from django.shortcuts import redirect, render

from bongusto.application.services import DashboardService
from bongusto.infrastructure.pdf_generator import crear_pdf_compuesto


class DashboardPageBuilder:
    """Clase pequena para armar contexto y reporte del dashboard."""

    def __init__(self):
        self.service = DashboardService()

    def construir_contexto(self):
        """Une estadisticas y ultimos registros."""
        contexto = {}
        contexto.update(self.service.obtener_estadisticas())
        contexto.update(self.service.obtener_ultimos())
        return contexto

    def contexto_vacio(self):
        """Devuelve una estructura segura si algo falla."""
        return {
            "metricas_resumen": [],
            "actividad_modulos": [],
            "usuarios_por_tipo": [],
            "resumen_operativo": [],
            "lineas_reserva": {"points": [], "polyline": "", "area": "", "max_value": 0},
            "calendario_dashboard": {"weekdays": [], "weeks": [], "today": None},
            "ultimos_menus": [],
            "ultimos_productos": [],
            "ultimas_musicas": [],
            "ultimas_reservas": [],
            "ultimos_registros": [],
            "resumen_general_total": 0,
            "resumen_general_porcentaje": 0,
            "total_usuarios": 0,
        }

    def construir_bloques_pdf(self, contexto):
        """Transforma el contexto en bloques simples para el generador PDF."""
        metricas_rows = self._filas_metricas(contexto.get("metricas_resumen", []))
        actividad_rows = self._filas_actividad(contexto.get("actividad_modulos", []))
        usuarios_rows = self._filas_usuarios(contexto.get("usuarios_por_tipo", []))
        reservas_rows = self._filas_reservas(contexto.get("lineas_reserva", {}))
        operativo_rows = self._filas_operativas(contexto.get("resumen_operativo", []))
        calendario_rows = self._filas_calendario(contexto.get("calendario_dashboard", {}))

        return [
            {
                "heading": "Resumen general del dashboard",
                "paragraph": (
                    f'El tablero consolida {contexto.get("resumen_general_total", 0)} registros principales '
                    f'y muestra una relacion central del {contexto.get("resumen_general_porcentaje", 0)}% '
                    "entre usuarios y reservas activas."
                ),
                "headers": ["Metrica", "Total", "Peso visual"],
                "rows": metricas_rows,
            },
            {
                "heading": "Carga por modulo",
                "paragraph": "Esta grafica compara el volumen relativo de datos entre usuarios, menus, productos, musica y reservas.",
                "headers": ["Modulo", "Total", "Participacion"],
                "rows": actividad_rows,
            },
            {
                "heading": "Tendencia de reservas",
                "paragraph": "La linea del dashboard refleja el comportamiento de reservas en los ultimos seis meses visibles.",
                "headers": ["Mes", "Reservas"],
                "rows": reservas_rows,
            },
            {
                "heading": "Distribucion de usuarios",
                "paragraph": "La grafica horizontal muestra como se reparte la base de usuarios por tipo dentro del sistema.",
                "headers": ["Tipo de usuario", "Total", "Participacion"],
                "rows": usuarios_rows,
            },
            {
                "heading": "Pulso del sistema",
                "paragraph": "Estos indicadores resumen el estado operativo actual del panel administrativo.",
                "headers": ["Indicador", "Valor", "Participacion"],
                "rows": operativo_rows,
            },
            {
                "heading": "Calendario operativo",
                "paragraph": (
                    f'Calendario de referencia para {contexto.get("calendario_dashboard", {}).get("month_name", "-")} '
                    f'de {contexto.get("calendario_dashboard", {}).get("year", "-")}.'
                ),
                "headers": contexto.get("calendario_dashboard", {}).get(
                    "weekdays",
                    ["D", "L", "M", "M", "J", "V", "S"],
                ),
                "rows": calendario_rows,
            },
            *self._bloques_ultimos_registros(contexto.get("ultimos_registros", [])),
        ]

    def _filas_metricas(self, metricas):
        filas = []
        for item in metricas:
            filas.append(
                [
                    item.get("titulo", "-"),
                    str(item.get("valor", 0)),
                    f'{item.get("porcentaje", 0)}%',
                ]
            )
        if not filas:
            filas.append(["Sin metricas", "0", "0%"])
        return filas

    def _filas_actividad(self, actividad):
        filas = []
        for item in actividad:
            filas.append(
                [
                    item.get("nombre", "-"),
                    str(item.get("valor", 0)),
                    f'{item.get("porcentaje", 0)}%',
                ]
            )
        if not filas:
            filas.append(["Sin modulos", "0", "0%"])
        return filas

    def _filas_usuarios(self, usuarios):
        filas = []
        for item in usuarios:
            filas.append(
                [
                    item.get("label", "-"),
                    str(item.get("total", 0)),
                    f'{item.get("porcentaje", 0)}%',
                ]
            )
        if not filas:
            filas.append(["Sin tipos", "0", "0%"])
        return filas

    def _filas_reservas(self, linea_reservas):
        filas = []
        for point in linea_reservas.get("points", []):
            filas.append([point.get("label", "-"), str(point.get("value", 0))])
        if not filas:
            filas.append(["Sin meses", "0"])
        return filas

    def _filas_operativas(self, resumen_operativo):
        filas = []
        for item in resumen_operativo:
            filas.append(
                [
                    item.get("label", "-"),
                    str(item.get("value", 0)),
                    f'{item.get("porcentaje", 0)}%',
                ]
            )
        if not filas:
            filas.append(["Sin pulso operativo", "0", "0%"])
        return filas

    def _filas_calendario(self, calendario_dashboard):
        filas = []
        for week in calendario_dashboard.get("weeks", []):
            fila = []
            for day in week:
                fila.append(str(day) if day else "-")
            filas.append(fila)
        if not filas:
            filas.append(["-", "-", "-", "-", "-", "-", "-"])
        return filas

    def _bloques_ultimos_registros(self, bloques):
        pdf_bloques = []
        for bloque in bloques:
            filas = []
            for texto in bloque.get("items", []):
                filas.append([texto])
            if not filas:
                filas.append(["Sin registros"])

            pdf_bloques.append(
                {
                    "heading": bloque.get("titulo", "Ultimos registros"),
                    "headers": [bloque.get("titulo", "Ultimos registros")],
                    "rows": filas,
                }
            )
        return pdf_bloques


page_builder = DashboardPageBuilder()


def _sesion_activa(request):
    """Valida si existe usuario en sesion."""
    return bool(request.session.get("usuario_id"))


def index(request):
    """Muestra la pantalla principal del dashboard."""
    if not _sesion_activa(request):
        return redirect("/login")

    try:
        contexto = page_builder.construir_contexto()
    except Exception:
        contexto = page_builder.contexto_vacio()

    return render(request, "dashboard/index.html", contexto)


def reporte(request):
    """Genera el PDF del dashboard."""
    if not _sesion_activa(request):
        return redirect("/login")

    try:
        contexto = page_builder.construir_contexto()
        bloques = page_builder.construir_bloques_pdf(contexto)
        pdf = crear_pdf_compuesto("Reporte de Dashboard", bloques)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="reporte_dashboard.pdf"'
        return response
    except Exception:
        return HttpResponse("No fue posible generar el reporte del dashboard.", status=500)
