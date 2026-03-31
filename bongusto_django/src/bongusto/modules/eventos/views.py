"""Vistas del modulo eventos en un estilo simple y directo."""

from collections import defaultdict
from datetime import datetime, time

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from bongusto.application.services import ReservaService, UsuarioService
from bongusto.domain.models import PedidoEncabezado, Reserva
from bongusto.infrastructure.pdf_generator import crear_pdf_compuesto
from bongusto.modules.shared.audit import registrar_movimiento


_service = ReservaService()
_usuario_service = UsuarioService()
_HORARIO_RESERVAS = [f"{hora:02d}:00" for hora in range(8, 22)]


class EventoPageHelper:
    """Agrupa pasos simples para que las vistas sean faciles de seguir."""

    def listar_usuarios(self):
        try:
            return _usuario_service.listar_todos()
        except Exception:
            return []

    def render_formulario(self, request, evento, accion, error=""):
        return render(
            request,
            "evento/form.html",
            {
                "evento": evento,
                "accion": accion,
                "usuarios": self.listar_usuarios(),
                "fecha_minima": timezone.localdate().isoformat(),
                "horarios_reserva": _HORARIO_RESERVAS,
                "error": error,
                "readonly": accion == "Ver",
            },
        )

    def leer_filtros(self, request):
        estado = request.GET.get("estado", "")
        fecha = request.GET.get("fecha", "")
        return {
            "estado": estado,
            "fecha": fecha,
            "fecha_busqueda": fecha or None,
        }

    def listar_eventos(self, filtros):
        try:
            return _service.listar_filtrado(
                estado=filtros["estado"],
                fecha=filtros["fecha_busqueda"],
            )
        except Exception:
            return []

    def buscar_evento(self, pk):
        try:
            return _service.buscar_por_id(pk)
        except Exception:
            return None

    def leer_fecha(self, valor):
        if not valor:
            return None
        try:
            return datetime.strptime(valor, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None

    def leer_hora(self, valor):
        if not valor:
            return None
        try:
            return datetime.strptime(valor, "%H:%M").time()
        except (TypeError, ValueError):
            return None

    def buscar_usuario(self, usuario_id):
        try:
            return _usuario_service.buscar_por_id(usuario_id)
        except Exception:
            return None

    def cargar_desde_post(self, request, evento):
        evento.fecha_reser = self.leer_fecha(request.POST.get("fecha_reser"))
        evento.hora_reser = (request.POST.get("hora_reser", "") or "").strip()
        evento.estado_reser = (request.POST.get("estado_reser", "activa") or "").strip().lower()
        evento.nombre_evento = (request.POST.get("nombre_evento", "") or "").strip()
        evento.detalle_evento = (request.POST.get("detalle_evento", "") or "").strip()
        return evento

    def validar(self, request, evento, accion):
        usuario_id = (request.POST.get("id_usuario", "") or "").strip()
        hora_valida = self.leer_hora(evento.hora_reser)

        if not usuario_id:
            return None, self.render_formulario(request, evento, accion, "Debes seleccionar un usuario registrado.")

        usuario = self.buscar_usuario(usuario_id)
        if not usuario:
            return None, self.render_formulario(request, evento, accion, "El usuario seleccionado no existe.")

        evento.id_usuario = usuario

        if not evento.nombre_evento:
            return None, self.render_formulario(request, evento, accion, "Debes escribir el nombre del evento.")

        if not evento.detalle_evento:
            return None, self.render_formulario(request, evento, accion, "Debes escribir el detalle del evento.")

        if evento.fecha_reser is None:
            return None, self.render_formulario(request, evento, accion, "Debes seleccionar una fecha valida.")

        if evento.fecha_reser < timezone.localdate():
            return None, self.render_formulario(request, evento, accion, "No puedes crear reservas en fechas pasadas.")

        if not evento.hora_reser:
            return None, self.render_formulario(request, evento, accion, "Debes seleccionar una hora.")

        if evento.hora_reser not in _HORARIO_RESERVAS or hora_valida is None:
            return None, self.render_formulario(request, evento, accion, "La hora debe estar entre 08:00 y 21:00.")

        if hora_valida < time(8, 0) or hora_valida > time(21, 30):
            return None, self.render_formulario(request, evento, accion, "La hora esta fuera del rango permitido.")

        if evento.estado_reser not in {"activa", "cancelada", "finalizada"}:
            return None, self.render_formulario(request, evento, accion, "El estado no es valido.")

        return evento, None

    def guardar(self, evento):
        _service.guardar(evento)

    def eliminar(self, pk):
        _service.eliminar(pk)

    def construir_reporte(self, eventos):
        eventos = list(eventos)
        tabla_principal = []
        eventos_por_mes = defaultdict(int)
        pedidos_por_fecha = self._pedidos_por_fecha()

        for evento in eventos:
            tabla_principal.append([
                str(evento.id_reser),
                self._nombre_responsable(evento),
                self._formatear_fecha(evento.fecha_reser),
                evento.hora_reser or "-",
                evento.estado_reser or "-",
                evento.detalle_evento or "-",
            ])

            if evento.fecha_reser:
                eventos_por_mes[evento.fecha_reser.strftime("%Y-%m")] += 1

        eventos_mes_rows = [[mes, str(total)] for mes, total in sorted(eventos_por_mes.items())] or [["Sin fechas", "0"]]

        ingresos_rows = []
        for evento in eventos:
            if evento.fecha_reser:
                ingresos_rows.append([
                    evento.nombre_evento or f"Evento {evento.id_reser}",
                    self._formatear_fecha(evento.fecha_reser),
                    f"${round(pedidos_por_fecha.get(evento.fecha_reser, 0), 2)}",
                ])

        if not ingresos_rows:
            ingresos_rows = [["Sin eventos", "-", "$0.0"]]

        return [
            {
                "heading": "Tabla reservas y estado del evento",
                "headers": ["ID", "Responsable", "Fecha", "Hora", "Estado", "Detalle"],
                "rows": tabla_principal or [["-", "-", "-", "-", "-", "-"]],
            },
            {
                "heading": "Eventos realizados por mes",
                "headers": ["Mes", "Total eventos"],
                "rows": eventos_mes_rows,
            },
            {
                "heading": "Ingresos estimados por fecha del evento",
                "paragraph": "Se toma el total de pedidos registrados en la misma fecha de la reserva.",
                "headers": ["Evento", "Fecha", "Ingresos del dia"],
                "rows": ingresos_rows[:10],
            },
        ]

    def _nombre_responsable(self, evento):
        if evento.nombre_evento:
            return evento.nombre_evento
        if evento.id_usuario:
            return evento.id_usuario.nombre_completo()
        return "-"

    def _formatear_fecha(self, fecha):
        if not fecha:
            return "-"
        return fecha.strftime("%d/%m/%Y")

    def _pedidos_por_fecha(self):
        pedidos_por_fecha = defaultdict(float)
        pedidos = PedidoEncabezado.objects.exclude(fecha_pedido__isnull=True).only("fecha_pedido", "total_pedido")
        for pedido in pedidos:
            if pedido.fecha_pedido:
                pedidos_por_fecha[pedido.fecha_pedido] += float(pedido.total_pedido or 0)
        return pedidos_por_fecha


_helper = EventoPageHelper()


def index(request):
    filtros = _helper.leer_filtros(request)
    eventos = _helper.listar_eventos(filtros)
    return render(request, "evento/index.html", {"eventos": eventos, "filtros": {"estado": filtros["estado"], "fecha": filtros["fecha"]}})


def nuevo(request):
    return _helper.render_formulario(request, Reserva(), "Crear")


def ver(request, pk):
    evento = _helper.buscar_evento(pk)
    if not evento:
        return redirect("/eventos")
    return _helper.render_formulario(request, evento, "Ver")


def store(request):
    if request.method != "POST":
        return redirect("/eventos")

    evento = _helper.cargar_desde_post(request, Reserva())
    evento, error = _helper.validar(request, evento, "Crear")
    if error:
        return error

    try:
        _helper.guardar(evento)
        registrar_movimiento(request, f"Creacion de evento para {evento.nombre_evento} el {evento.fecha_reser}")
        return redirect("/eventos")
    except Exception:
        return _helper.render_formulario(request, evento, "Crear", "Error al guardar el evento.")


def editar(request, pk):
    evento = _helper.buscar_evento(pk)
    if not evento:
        return redirect("/eventos")
    return _helper.render_formulario(request, evento, "Editar")


def update(request, pk):
    if request.method != "POST":
        return redirect("/eventos")

    evento = _helper.buscar_evento(pk)
    if not evento:
        return redirect("/eventos")

    evento = _helper.cargar_desde_post(request, evento)
    evento, error = _helper.validar(request, evento, "Editar")
    if error:
        return error

    try:
        _helper.guardar(evento)
        registrar_movimiento(request, f"Actualizacion de evento {evento.nombre_evento or evento.id_reser}.")
        return redirect("/eventos")
    except Exception:
        return _helper.render_formulario(request, evento, "Editar", "Error al actualizar el evento.")


def eliminar(request, pk):
    try:
        evento = _helper.buscar_evento(pk)
        _helper.eliminar(pk)
        if evento:
            registrar_movimiento(request, f"Cancelacion o eliminacion de evento {evento.nombre_evento or evento.id_reser}.")
    except Exception:
        pass
    return redirect("/eventos")


def pdf(request):
    try:
        filtros = _helper.leer_filtros(request)
        eventos = _helper.listar_eventos(filtros)
        data = crear_pdf_compuesto("Reporte de Eventos", _helper.construir_reporte(eventos))
        response = HttpResponse(data, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="reporte_reservas.pdf"'
        return response
    except Exception:
        return HttpResponse("Error generando el PDF.", status=500)
