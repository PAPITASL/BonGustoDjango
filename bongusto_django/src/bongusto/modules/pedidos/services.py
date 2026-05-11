"""Servicios del modulo `pedidos`, aqui se maneja toda la logica de pedidos (encabezado y detalles)."""


# Se importa transaction para manejar procesos seguros en base de datos
from django.db import connection, transaction
from django.utils import timezone

# Modelos que se van a usar
from bongusto.domain.models import PedidoDetalle, PedidoEncabezado, Producto, Usuario
from bongusto.modules.shared.table_state import MesaStateService



# Clase principal donde va toda la logica de pedidos
class PedidoService:
    def __init__(self):
        self.mesa_service = MesaStateService()

    def _pedido_activo_para_usuario_y_mesa(self, mesa, usuario):
        pedido = getattr(mesa, "pedido_actual", None)
        if pedido and pedido.id_usuario_id == usuario.id_usuario and getattr(pedido, "estado_pedido", "abierto") != "finalizado":
            return pedido
        return None

    def asegurar_esquema(self):
        """Agrega columnas operativas faltantes en instalaciones existentes."""
        with connection.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM pedido_encabezado LIKE 'tipo_pedido'")
            if not cursor.fetchone():
                cursor.execute(
                    """
                    ALTER TABLE pedido_encabezado
                    ADD COLUMN tipo_pedido VARCHAR(20) NOT NULL DEFAULT 'restaurante'
                    AFTER id_restaurante
                    """
                )
            cursor.execute("SHOW COLUMNS FROM pedido_encabezado LIKE 'mesa_id'")
            tiene_mesa_id = cursor.fetchone()
            if not tiene_mesa_id:
                cursor.execute(
                    """
                    ALTER TABLE pedido_encabezado
                    ADD COLUMN mesa_id INT NULL AFTER id_restaurante
                    """
                )
            cursor.execute("SHOW COLUMNS FROM pedido_encabezado LIKE 'estado_pedido'")
            if not cursor.fetchone():
                cursor.execute(
                    """
                    ALTER TABLE pedido_encabezado
                    ADD COLUMN estado_pedido VARCHAR(20) NOT NULL DEFAULT 'abierto'
                    """
                )
            cursor.execute("SHOW COLUMNS FROM pedido_encabezado LIKE 'fecha_finalizacion'")
            if not cursor.fetchone():
                cursor.execute(
                    """
                    ALTER TABLE pedido_encabezado
                    ADD COLUMN fecha_finalizacion DATETIME(6) NULL
                    """
                )
            cursor.execute(
                """
                UPDATE pedido_encabezado
                SET estado_pedido = COALESCE(NULLIF(estado_pedido, ''), 'abierto')
                """
            )
            cursor.execute(
                """
                UPDATE pedido_encabezado
                SET tipo_pedido = COALESCE(NULLIF(tipo_pedido, ''), 'restaurante')
                """
            )


    # Trae todos los pedidos con su usuario y detalles
    def listar_pedidos(self):
        self.asegurar_esquema()
        return (
            PedidoEncabezado.objects.select_related("id_usuario")
            .prefetch_related("pedidodetalle_set")
            .all()
            .order_by("-id_pedido")
        )


    # Trae los pedidos de un usuario especifico
    def listar_por_usuario(self, usuario_id):
        self.asegurar_esquema()
        return (
            PedidoEncabezado.objects.select_related("id_usuario")
            .prefetch_related("pedidodetalle_set")
            .filter(id_usuario_id=usuario_id)
            .order_by("-id_pedido")
        )


    # Busca un pedido por su id
    def obtener_pedido(self, pk):
        self.asegurar_esquema()
        return PedidoEncabezado.objects.filter(pk=pk).first()


    # Crea un pedido simple
    def crear_pedido(self, pedido):
        pedido.save()
        return pedido


    # Crea un pedido completo con sus productos
    @transaction.atomic
    def crear_pedido_con_detalles(self, data):
        self.asegurar_esquema()
        usuario_id = data.get("id_usuario")
        mesa_id = data.get("mesa_id")
        items = data.get("items") or []
        tipo_pedido = (data.get("tipo_pedido") or "restaurante").strip().lower()
        if tipo_pedido not in {"restaurante", "para_llevar"}:
            tipo_pedido = "restaurante"

        # Validaciones basicas
        if not usuario_id:
            raise ValueError("id_usuario es obligatorio")

        usuario = Usuario.objects.filter(pk=usuario_id).first()
        if not usuario:
            raise ValueError("Usuario no encontrado")

        mesa = None
        if tipo_pedido == "restaurante":
            if not mesa_id:
                raise ValueError("Debes seleccionar una mesa valida antes de pedir")

            mesa = self.mesa_service.buscar_modelo(mesa_id)
            if not mesa:
                raise ValueError("La mesa indicada no existe")
            if not mesa.activa or mesa.estado == mesa.ESTADO_BLOQUEADA:
                raise ValueError("La mesa no esta disponible")
            if mesa.usuario_actual_id and mesa.usuario_actual_id != usuario.id_usuario:
                raise ValueError("La mesa pertenece a otro cliente")
            pedido_existente = self._pedido_activo_para_usuario_y_mesa(mesa, usuario)
            if mesa.pedido_actual_id and not pedido_existente:
                raise ValueError("La mesa ya tiene un pedido activo")

            pedido = pedido_existente
            if pedido:
                pedido.pedidodetalle_set.all().delete()
                pedido.id_restaurante = data.get("id_restaurante") or pedido.id_restaurante or 1
                pedido.tipo_pedido = "restaurante"
                pedido.mesa = mesa
                pedido.id_usuario = usuario
                pedido.fecha_pedido = data.get("fecha_pedido") or pedido.fecha_pedido
                pedido.estado_pedido = "abierto"
                pedido.fecha_finalizacion = None
                pedido.save(update_fields=["id_restaurante", "tipo_pedido", "mesa", "id_usuario", "fecha_pedido", "estado_pedido", "fecha_finalizacion"])
            else:
                if not items:
                    raise ValueError("El pedido debe incluir items")
                pedido = PedidoEncabezado(
                    id_usuario=usuario,
                    id_restaurante=data.get("id_restaurante") or 1,
                    tipo_pedido="restaurante",
                    mesa=mesa,
                    fecha_pedido=data.get("fecha_pedido"),
                    total_pedido=0,
                    estado_pedido="abierto",
                    fecha_finalizacion=None,
                )
                pedido.save()
        else:
            if not items:
                raise ValueError("El pedido debe incluir items")
            pedido = PedidoEncabezado(
                id_usuario=usuario,
                id_restaurante=data.get("id_restaurante") or 1,
                tipo_pedido="para_llevar",
                mesa=None,
                fecha_pedido=data.get("fecha_pedido"),
                total_pedido=0,
                estado_pedido="abierto",
                fecha_finalizacion=None,
            )
            pedido.save()

        total_calculado = 0

        # Recorrer los productos del pedido
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

            # Crear detalle del pedido
            detalle = PedidoDetalle(
                id_pedido=pedido,
                id_producto=producto.id_producto,
                cantidad=cantidad,
                precio=precio,
            )
            detalle.save()

            total_calculado += float(precio) * cantidad

        # El total real del pedido siempre sale de los items persistidos.
        pedido.total_pedido = total_calculado
        pedido.save(update_fields=["total_pedido", "estado_pedido", "fecha_finalizacion"])

        if items and mesa is not None:
            self.mesa_service.ocupar_con_pedido(mesa, pedido, cliente=usuario)
        return pedido


    # Elimina un pedido por id
    def eliminar(self, pk):
        PedidoEncabezado.objects.filter(pk=pk).delete()


# Aqui se define lo que se exporta del servicio
__all__ = ["PedidoService", "PedidoEncabezado"]
