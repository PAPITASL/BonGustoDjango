"""Servicios del modulo `pedidos`. Aqui se maneja la logica principal de encabezados, detalles y flujo de pedidos."""


# ===== Importaciones | Dependencias necesarias para el funcionamiento del modulo `pedidos`. =====
from django.db import transaction

from bongusto.domain.models import PedidoDetalle, PedidoEncabezado, Producto, Usuario



# ===== Clase `PedidoService` | Modulo `pedidos` | Contiene la logica de negocio para gestionar pedidos. =====
class PedidoService:


    # ===== Funcion `listar_pedidos` | Modulo `pedidos` | Retorna todos los pedidos con sus relaciones principales. =====
    def listar_pedidos(self):
        return (
            PedidoEncabezado.objects.select_related("id_usuario")
            .prefetch_related("pedidodetalle_set")
            .all()
            .order_by("-id_pedido")
        )


    # ===== Funcion `listar_por_usuario` | Modulo `pedidos` | Retorna pedidos filtrados por usuario. =====
    def listar_por_usuario(self, usuario_id):
        return (
            PedidoEncabezado.objects.select_related("id_usuario")
            .prefetch_related("pedidodetalle_set")
            .filter(id_usuario_id=usuario_id)
            .order_by("-id_pedido")
        )


    # ===== Funcion `obtener_pedido` | Modulo `pedidos` | Busca un pedido especifico por ID. =====
    def obtener_pedido(self, pk):
        return PedidoEncabezado.objects.filter(pk=pk).first()


    # ===== Funcion `crear_pedido` | Modulo `pedidos` | Guarda un pedido simple. =====
    def crear_pedido(self, pedido):
        pedido.save()
        return pedido


    # ===== Funcion `crear_pedido_con_detalles` | Modulo `pedidos` | Crea un pedido completo con sus items asociados. =====
    @transaction.atomic
    def crear_pedido_con_detalles(self, data):
        usuario_id = data.get("id_usuario")
        items = data.get("items") or []

        # Validaciones basicas
        if not usuario_id:
            raise ValueError("id_usuario es obligatorio")

        if not items:
            raise ValueError("El pedido debe incluir items")

        usuario = Usuario.objects.filter(pk=usuario_id).first()
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Crear encabezado
        pedido = PedidoEncabezado(
            id_usuario=usuario,
            id_restaurante=data.get("id_restaurante") or 1,
            fecha_pedido=data.get("fecha_pedido"),
            total_pedido=data.get("total_pedido") or 0,
        )
        pedido.save()

        total_calculado = 0

        # Crear detalles del pedido
        for item in items:
            producto_id = item.get("id_producto")
            cantidad = int(item.get("cantidad") or 0)

            producto = Producto.objects.filter(pk=producto_id).first()
            if not producto:
                raise ValueError(f"Producto no encontrado: {producto_id}")

            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a cero")

            precio = item.get("precio")
            if precio in (None, ""):
                precio = producto.precio_producto or 0

            detalle = PedidoDetalle(
                id_pedido=pedido,
                id_producto=producto.id_producto,
                cantidad=cantidad,
                precio=precio,
            )
            detalle.save()

            total_calculado += float(precio) * cantidad

        # Ajustar total si no viene definido
        if not data.get("total_pedido"):
            pedido.total_pedido = total_calculado
            pedido.save(update_fields=["total_pedido"])

        return pedido


    # ===== Funcion `eliminar` | Modulo `pedidos` | Elimina un pedido por ID. =====
    def eliminar(self, pk):
        PedidoEncabezado.objects.filter(pk=pk).delete()



# ===== Exportacion | Modulo `pedidos` | Define que elementos se exponen desde este archivo. =====
__all__ = ["PedidoService", "PedidoEncabezado"]