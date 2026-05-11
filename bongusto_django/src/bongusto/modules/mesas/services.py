"""Servicios del modulo mesas en vivo para admin, mesero y cliente."""

import json
from datetime import date

from bongusto.domain.models import MensajeChat, PedidoEncabezado
from bongusto.modules.pedidos.payment_services import SolicitudPagoService
from bongusto.modules.pedidos.services import PedidoService
from bongusto.modules.shared.table_state import MesaStateService


class OperacionMesasService:
    """Construye snapshots operativos consistentes para las tres aplicaciones."""

    def __init__(self):
        self.mesa_service = MesaStateService()
        self.pago_service = SolicitudPagoService()
        self.pedido_service = PedidoService()

    def _extraer_estado_llamado(self, mensaje):
        try:
            payload = json.loads(mensaje.mensaje or "{}")
        except Exception:
            payload = {}
        return (payload.get("estado") or "pendiente").strip().lower(), payload

    def _snapshot_base(self):
        self.pedido_service.asegurar_esquema()
        mesas = self.mesa_service.listar()
        pedidos = list(
            PedidoEncabezado.objects.select_related("id_usuario")
            .prefetch_related("pedidodetalle_set")
            .order_by("-id_pedido")[:80]
        )
        llamados = list(
            MensajeChat.objects.filter(destinatario="mesero_call")
            .order_by("-fecha")[:80]
        )
        pagos_por_mesa = self.pago_service.solicitud_activa_por_mesa()

        resumen_por_mesa = {}
        mesas_por_id = {}
        for mesa in mesas:
            mesa_id = mesa.get("id")
            if not mesa_id:
                continue
            mesas_por_id[mesa_id] = mesa
            resumen_por_mesa[mesa_id] = {"pedidos": 0, "total": 0.0, "total_pendiente": 0.0}
            pago = pagos_por_mesa.get(mesa.get("id"))
            if pago:
                mesa["pago"] = pago

        pedidos_payload = []
        pedidos_para_llevar = []
        total_hoy = 0
        today = date.today()
        solicitudes_por_pedido = {
            item.get("id_pedido"): item
            for item in self.pago_service.listar()
            if item.get("id_pedido") and item.get("estado") != "finalizada"
        }
        for pedido in pedidos:
            usuario = getattr(pedido, "id_usuario", None)
            usuario_id = getattr(usuario, "id_usuario", None) if usuario else None
            mesa_id = getattr(pedido, "mesa_id", None)
            mesa_cache = self.mesa_service.detalle(mesa_id) if mesa_id else {}
            tipo_pedido = (getattr(pedido, "tipo_pedido", "restaurante") or "").strip().lower()
            mesa_label = (
                "Para llevar"
                if tipo_pedido == "para_llevar"
                else mesa_cache.get("etiqueta") or (f"Mesa {mesa_cache.get('numero_mesa') or mesa_id}" if mesa_id else "Sin mesa")
            )
            total = float(pedido.total_pedido or 0)
            mesa_actual = mesas_por_id.get(mesa_id) or {}
            estado_mesa = (mesa_actual.get("estado") or "").strip().lower()
            pedido_actual_id = mesa_actual.get("pedido_actual_id") or mesa_actual.get("pedido_actual")
            if (
                mesa_id in resumen_por_mesa
                and pedido_actual_id
                and int(pedido_actual_id) == int(pedido.id_pedido)
                and estado_mesa not in {"libre", "bloqueada"}
            ):
                resumen_por_mesa[mesa_id]["pedidos"] += 1
                resumen_por_mesa[mesa_id]["total"] += total
                resumen_por_mesa[mesa_id]["total_pendiente"] += total

            if getattr(pedido, "fecha_pedido", None) == today:
                total_hoy += 1

            pedido_payload = {
                "id_pedido": pedido.id_pedido,
                "id_usuario": usuario_id,
                "cliente_nombre": usuario.nombre_completo() if usuario else "",
                "mesa_id": mesa_id,
                "mesa_label": mesa_label,
                "tipo_pedido": tipo_pedido,
                "total_pedido": total,
                "fecha_pedido": str(pedido.fecha_pedido) if pedido.fecha_pedido else "",
                "estado": getattr(pedido, "estado_pedido", "abierto"),
            }
            pago_pedido = solicitudes_por_pedido.get(pedido.id_pedido)
            if pago_pedido:
                pedido_payload["pago"] = {
                    "id_solicitud_pago": pago_pedido.get("id_solicitud_pago"),
                    "metodo_pago": pago_pedido.get("metodo_pago"),
                    "estado": pago_pedido.get("estado"),
                    "finalizado_en": pago_pedido.get("finalizado_en"),
                }
            pedidos_payload.append(pedido_payload)
            if tipo_pedido == "para_llevar" and getattr(pedido, "estado_pedido", "abierto") != "finalizado":
                pedidos_para_llevar.append(pedido_payload)

        llamados_payload = []
        pendientes = 0
        for llamado in llamados:
            estado, payload = self._extraer_estado_llamado(llamado)
            if estado == "pendiente":
                pendientes += 1
            llamados_payload.append(
                {
                    "id": llamado.id,
                    "id_usuario": payload.get("id_usuario"),
                    "mesa_id": payload.get("mesa_id"),
                    "estado": estado,
                    "mensaje": payload.get("mensaje") or "",
                    "fecha": llamado.fecha.isoformat() if llamado.fecha else "",
                }
            )

        return {
            "kpis": {
                "mesas_totales": len(mesas),
                "mesas_ocupadas": sum(
                    1 for mesa in mesas if (mesa.get("estado") or "").strip().lower() != "libre"
                ),
                "pedidos_hoy": total_hoy,
                "pedidos_totales": len(pedidos_payload),
                "llamados_pendientes": pendientes,
                "pagos_pendientes": sum(1 for item in pagos_por_mesa.values() if item.get("estado") == "pendiente"),
            },
            "mesas": mesas,
            "resumen_por_mesa": resumen_por_mesa,
            "ultimos_pedidos": pedidos_payload,
            "pedidos_para_llevar": pedidos_para_llevar,
            "llamados": llamados_payload,
            "solicitudes_pago": list(pagos_por_mesa.values()),
        }

    def snapshot_para_usuario(self, usuario):
        """Retorna snapshot filtrado por rol para proteger datos sensibles."""
        base = self._snapshot_base()
        tipo = (getattr(usuario, "tipo_usuario", "") or "").strip().lower()

        if tipo in {"administrador", "mesero"}:
            return base

        if tipo == "cliente":
            user_id = getattr(usuario, "id_usuario", None)
            mesa_cliente = self.mesa_service.mesa_por_usuario(user_id)
            mesa_id = mesa_cliente.get("id") if mesa_cliente else None

            pedidos_cliente = [p for p in base["ultimos_pedidos"] if p.get("id_usuario") == user_id]
            llamados_cliente = [l for l in base["llamados"] if l.get("id_usuario") == user_id]

            resumen = {}
            mesas = []
            if mesa_cliente:
                mesas = [mesa_cliente]
                resumen[mesa_id] = base["resumen_por_mesa"].get(mesa_id, {"pedidos": 0, "total": 0.0})

            return {
                "kpis": {
                    "mesas_totales": 1 if mesa_cliente else 0,
                    "mesas_ocupadas": 1 if mesa_cliente and (mesa_cliente.get("estado") or "").lower() != "libre" else 0,
                    "pedidos_hoy": sum(1 for p in pedidos_cliente if p.get("fecha_pedido") == str(date.today())),
                    "pedidos_totales": len(pedidos_cliente),
                    "llamados_pendientes": sum(1 for l in llamados_cliente if l.get("estado") == "pendiente"),
                    "pagos_pendientes": sum(
                        1
                        for item in base.get("solicitudes_pago", [])
                        if item.get("id_usuario") == user_id and item.get("estado") == "pendiente"
                    ),
                },
                "mesas": mesas,
                "resumen_por_mesa": resumen,
                "ultimos_pedidos": pedidos_cliente[:20],
                "pedidos_para_llevar": [item for item in base.get("pedidos_para_llevar", []) if item.get("id_usuario") == user_id][:20],
                "llamados": llamados_cliente[:20],
                "solicitudes_pago": [
                    item for item in base.get("solicitudes_pago", []) if item.get("id_usuario") == user_id
                ][:20],
            }

        return {"kpis": {}, "mesas": [], "resumen_por_mesa": {}, "ultimos_pedidos": [], "pedidos_para_llevar": [], "llamados": [], "solicitudes_pago": []}


__all__ = ["OperacionMesasService"]
