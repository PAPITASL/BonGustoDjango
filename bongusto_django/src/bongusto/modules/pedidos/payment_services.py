"""Servicios para coordinar solicitudes de pago sin pasarela externa."""

from django.db import connection, transaction
from django.utils import timezone

from bongusto.domain.models import PedidoEncabezado, SolicitudPago, Usuario
from bongusto.modules.shared.realtime import emitir_evento_operacion
from bongusto.modules.shared.table_state import MesaStateService


class SolicitudPagoService:
    """Crea, consulta y actualiza solicitudes de pago en mesa."""

    METODOS = {
        "tarjeta": "Tarjeta / datafono",
        "datafono": "Tarjeta / datafono",
        "tarjeta_datafono": "Tarjeta / datafono",
        "efectivo": "Efectivo",
        "otro": "Otro metodo de pago",
        "otro_metodo": "Otro metodo de pago",
    }
    ESTADOS = {"pendiente", "atendida", "finalizada"}

    def __init__(self):
        self.mesa_service = MesaStateService()

    def asegurar_tabla(self):
        """Crea la tabla si la base aun no la tiene."""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS solicitudes_pago (
                    id_solicitud_pago INT AUTO_INCREMENT PRIMARY KEY,
                    id_pedido INT NULL,
                    id_usuario INT NULL,
                    mesa_id INT NULL,
                    metodo_pago VARCHAR(40) NOT NULL,
                    estado VARCHAR(30) NOT NULL DEFAULT 'pendiente',
                    id_mesero_atendio INT NULL,
                    fecha_creacion DATETIME(6) NOT NULL,
                    fecha_actualizacion DATETIME(6) NOT NULL,
                    finalizado_en DATETIME(6) NULL,
                    notas LONGTEXT NULL,
                    INDEX solicitudes_pago_mesa_idx (mesa_id),
                    INDEX solicitudes_pago_estado_idx (estado),
                    INDEX solicitudes_pago_pedido_idx (id_pedido),
                    INDEX solicitudes_pago_usuario_idx (id_usuario)
                )
                """
            )

    def normalizar_metodo(self, metodo):
        clave = (metodo or "").strip().lower().replace("/", "_").replace(" ", "_")
        if clave not in self.METODOS:
            raise ValueError("Metodo de pago no permitido")
        return self.METODOS[clave]

    def normalizar_estado(self, estado):
        valor = (estado or "").strip().lower()
        if valor not in self.ESTADOS:
            raise ValueError("Estado de solicitud de pago no permitido")
        return valor

    def _pedido_para_usuario(self, usuario, pedido_id=None, mesa_id=None):
        queryset = (
            PedidoEncabezado.objects.select_related("id_usuario", "mesa")
            .filter(id_usuario=usuario)
            .exclude(estado_pedido="finalizado")
        )
        if pedido_id:
            return queryset.filter(pk=pedido_id).first()
        if mesa_id:
            pedido_mesa = queryset.filter(mesa_id=mesa_id).order_by("-id_pedido").first()
            if pedido_mesa:
                return pedido_mesa
        pedido_activo = queryset.exclude(estado_pedido="finalizado").order_by("-id_pedido").first()
        if pedido_activo:
            return pedido_activo
        return queryset.order_by("-id_pedido").first()

    def _mesa_para_usuario(self, usuario, mesa_id=None):
        if mesa_id:
            mesa = self.mesa_service.buscar_modelo(mesa_id)
            if mesa and mesa.pedido_actual_id and getattr(mesa.pedido_actual, "estado_pedido", "abierto") != "finalizado":
                return mesa
        mesa_actual = self.mesa_service.mesa_por_usuario(usuario.id_usuario)
        if mesa_actual:
            return self.mesa_service.buscar_modelo(mesa_actual.get("id"))
        return None

    def solicitud_to_dict(self, solicitud):
        pedido = solicitud.id_pedido
        usuario = solicitud.id_usuario
        mesero = solicitud.atendido_por
        mesa_id = solicitud.mesa_id or getattr(pedido, "mesa_id", None)
        mesa_detalle = self.mesa_service.detalle(mesa_id) if mesa_id else None
        tipo_pedido = (getattr(pedido, "tipo_pedido", "restaurante") or "").strip().lower()
        mesa_label = (
            "Para llevar"
            if tipo_pedido == "para_llevar"
            else (mesa_detalle or {}).get("etiqueta") or (f"Mesa {solicitud.mesa_id}" if solicitud.mesa_id else "Sin mesa")
        )
        return {
            "id_solicitud_pago": solicitud.id_solicitud_pago,
            "id_pedido": pedido.id_pedido if pedido else None,
            "id_usuario": usuario.id_usuario if usuario else None,
            "cliente_nombre": usuario.nombre_completo() if usuario else "",
            "cliente_correo": usuario.correo if usuario else "",
            "mesa_id": mesa_id,
            "mesa_label": mesa_label,
            "tipo_pedido": tipo_pedido,
            "metodo_pago": solicitud.metodo_pago,
            "estado": solicitud.estado,
            "atendido_por": mesero.nombre_completo() if mesero else "",
            "id_mesero_atendio": mesero.id_usuario if mesero else None,
            "fecha_creacion": solicitud.fecha_creacion.isoformat() if solicitud.fecha_creacion else "",
            "fecha_actualizacion": solicitud.fecha_actualizacion.isoformat() if solicitud.fecha_actualizacion else "",
            "finalizado_en": solicitud.finalizado_en.isoformat() if solicitud.finalizado_en else "",
            "notas": solicitud.notas or "",
            "mensaje_operativo": self.mensaje_operativo(solicitud.metodo_pago),
            "total_pedido": float((pedido.total_pedido or 0)) if pedido else 0.0,
        }

    def mensaje_operativo(self, metodo):
        metodo_lower = (metodo or "").lower()
        if "tarjeta" in metodo_lower or "datafono" in metodo_lower:
            return "Llevar datafono a la mesa."
        if "efectivo" in metodo_lower:
            return "Llevar factura y cambio si aplica."
        return "Confirmar con el cliente el metodo de pago."

    @transaction.atomic
    def crear_solicitud(self, usuario, metodo_pago, pedido_id=None, mesa_id=None):
        self.asegurar_tabla()
        metodo = self.normalizar_metodo(metodo_pago)
        mesa = self._mesa_para_usuario(usuario, mesa_id)
        mesa_id_final = getattr(mesa, "id", None) or int(mesa_id or 0) or None
        pedido = self._pedido_para_usuario(usuario, pedido_id, mesa_id=mesa_id_final)
        tipo_pedido = (getattr(pedido, "tipo_pedido", "restaurante") or "restaurante").strip().lower()

        if not pedido:
            raise ValueError("No existe un pedido activo para solicitar el pago")
        if tipo_pedido == "restaurante":
            if not mesa_id_final:
                raise ValueError("El cliente no tiene una mesa asignada")
            if getattr(pedido, "mesa_id", None) and int(pedido.mesa_id or 0) != int(mesa_id_final):
                raise ValueError("El pedido activo no corresponde a la mesa seleccionada")
            if getattr(pedido, "estado_pedido", "abierto") == "finalizado":
                raise ValueError("El pedido activo ya fue finalizado")
        else:
            mesa_id_final = None
            mesa = None

        solicitud_activa = (
            SolicitudPago.objects.filter(mesa_id=mesa_id_final)
            .exclude(estado="finalizada")
            .order_by("-fecha_creacion")
            .first()
            if mesa_id_final
            else None
        )
        if solicitud_activa:
            raise ValueError("La mesa ya tiene una solicitud de pago en proceso")

        solicitud = SolicitudPago.objects.create(
            id_pedido=pedido,
            id_usuario=usuario,
            mesa_id=mesa_id_final,
            metodo_pago=metodo,
            estado="pendiente",
            notas="BonGusto solo coordina la solicitud; el pago se realiza con el mesero.",
        )

        mesa_actualizada = self._marcar_mesa_con_pago(mesa_id_final, solicitud) if mesa_id_final else None
        payload = self.solicitud_to_dict(solicitud)
        emitir_evento_operacion("solicitud_pago_creada", payload)
        if mesa_actualizada:
            emitir_evento_operacion("estado_mesa_actualizado", mesa_actualizada)
            emitir_evento_operacion("mesa_actualizada", mesa_actualizada)
        return solicitud

    def listar(self, estado=None):
        self.asegurar_tabla()
        qs = SolicitudPago.objects.select_related("id_pedido", "id_usuario", "atendido_por").all()
        estado_normalizado = (estado or "").strip().lower()
        if estado_normalizado:
            qs = qs.filter(estado=estado_normalizado)
        return [self.solicitud_to_dict(item) for item in qs[:80]]

    @transaction.atomic
    def actualizar_estado(self, solicitud_id, estado, mesero=None):
        self.asegurar_tabla()
        estado_normalizado = self.normalizar_estado(estado)
        solicitud = SolicitudPago.objects.select_related("id_pedido", "id_usuario", "atendido_por").filter(
            pk=solicitud_id
        ).first()
        if not solicitud:
            return None

        solicitud.estado = estado_normalizado
        if mesero and (mesero.tipo_usuario or "").strip().lower() in {"mesero", "administrador"}:
            solicitud.atendido_por = mesero
        if estado_normalizado == "finalizada":
            solicitud.finalizado_en = timezone.now()
        solicitud.save()

        pedido_finalizado = None
        if estado_normalizado == "finalizada":
            pedido_finalizado = self._finalizar_pedido_de_solicitud(solicitud)

        mesa_actualizada = self._marcar_mesa_con_pago(solicitud.mesa_id, solicitud)
        payload = self.solicitud_to_dict(solicitud)
        emitir_evento_operacion("pago_confirmado" if estado_normalizado == "finalizada" else "pago_actualizado", payload)
        if pedido_finalizado:
            emitir_evento_operacion(
                "pedido_actualizado",
                {
                    "id_pedido": pedido_finalizado.id_pedido,
                    "id_usuario": pedido_finalizado.id_usuario_id,
                    "mesa_id": pedido_finalizado.mesa_id,
                    "tipo_pedido": getattr(pedido_finalizado, "tipo_pedido", "restaurante"),
                    "estado": pedido_finalizado.estado_pedido,
                    "total_pedido": float(pedido_finalizado.total_pedido or 0),
                    "fecha_finalizacion": (
                        pedido_finalizado.fecha_finalizacion.isoformat()
                        if getattr(pedido_finalizado, "fecha_finalizacion", None)
                        else ""
                    ),
                },
            )
        if mesa_actualizada:
            emitir_evento_operacion("estado_mesa_actualizado", mesa_actualizada)
            emitir_evento_operacion("mesa_actualizada", mesa_actualizada)
        return solicitud

    def solicitud_activa_por_mesa(self):
        self.asegurar_tabla()
        solicitudes = SolicitudPago.objects.select_related("id_pedido", "id_usuario", "atendido_por").exclude(
            estado="finalizada"
        )
        resultado = {}
        for solicitud in solicitudes.order_by("-fecha_creacion"):
            if solicitud.mesa_id and solicitud.mesa_id not in resultado:
                resultado[solicitud.mesa_id] = self.solicitud_to_dict(solicitud)
        return resultado

    def _marcar_mesa_con_pago(self, mesa_id, solicitud):
        mesa_id = int(mesa_id or 0)
        if not mesa_id:
            return None

        if solicitud.estado == "finalizada":
            self.mesa_service.confirmar_pago(mesa_id, solicitud=solicitud, mesero=solicitud.atendido_por)
        else:
            self.mesa_service.registrar_solicitud_pago(mesa_id, solicitud)
        return self.mesa_service.detalle(mesa_id)

    def _finalizar_pedido_de_solicitud(self, solicitud):
        pedido = solicitud.id_pedido
        if not pedido or getattr(pedido, "estado_pedido", "abierto") == "finalizado":
            return None
        pedido.estado_pedido = "finalizado"
        pedido.fecha_finalizacion = pedido.fecha_finalizacion or timezone.now()
        pedido.save(update_fields=["estado_pedido", "fecha_finalizacion"])
        return pedido


__all__ = ["SolicitudPagoService"]
