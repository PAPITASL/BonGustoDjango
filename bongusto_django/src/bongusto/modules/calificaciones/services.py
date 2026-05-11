"""
Servicios del módulo calificaciones.
Aquí se maneja la lógica relacionada con las calificaciones de los clientes.
"""
# Permite ejecutar SQL directamente (cuando no usamos migraciones)
from django.db import connection, IntegrityError
# Para hacer filtros más flexibles (OR, AND, etc.)
from django.db.models import Q
# Modelos que se usan en este módulo
from bongusto.domain.models import CalificacionCliente, PedidoEncabezado, Usuario

class CalificacionService:
    ESTADOS_CALIFICABLES = {"pagado", "entregado", "finalizado"}

    # Se asegura de que la tabla exista en la base de datos
    def asegurar_tabla(self):

        # cursor permite ejecutar SQL manualmente
        with connection.cursor() as cursor:

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS calificaciones_clientes (
                    id_calificacion INTEGER PRIMARY KEY AUTO_INCREMENT,
                    id_usuario INTEGER NULL,
                    id_pedido INTEGER NULL,
                    calificacion_comida SMALLINT NULL,
                    calificacion_servicio SMALLINT NULL,
                    calificacion_ambiente SMALLINT NULL,
                    observaciones TEXT NULL,
                    fecha_calificacion DATETIME NULL
                )
                """
            )

    # Trae todas las calificaciones
    def listar_todas(self):

        # Primero se asegura que la tabla exista
        self.asegurar_tabla()

        # select_related mejora el rendimiento trayendo usuario y pedido en la misma consulta
        return (
            CalificacionCliente.objects
            .select_related("id_usuario", "id_pedido")
            .all()
            .order_by("-fecha_calificacion", "-id_calificacion")
        )

    # Lista calificaciones aplicando filtros
    def listar_filtrado(self, usuario=None, puntaje=None):

        # Parte de todos los registros
        qs = self.listar_todas()

        # Filtro por nombre o apellido del usuario
        if usuario:
            qs = qs.filter(
                Q(id_usuario__nombre__icontains=usuario) |
                Q(id_usuario__apellido__icontains=usuario)
            )

        # Filtro por puntaje exacto de estrellas.
        if puntaje:
            try:
                puntaje_int = int(puntaje)
            except (TypeError, ValueError):
                puntaje_int = None

            # Como el promedio no está en la base de datos sino calculado en Python,
            # el filtro se hace en memoria. Se compara con el promedio redondeado
            # para que 4.6 cuente como 5 estrellas y 4.4 como 4 estrellas.
            if puntaje_int:
                qs = [
                    item for item in qs
                    if int(round(float(item.promedio or 0))) == puntaje_int
                ]

        return qs

    # Busca una calificación por su id
    def buscar_por_id(self, pk):

        # Asegura la existencia de la tabla antes de consultar
        self.asegurar_tabla()

        return (
            CalificacionCliente.objects
            .select_related("id_usuario", "id_pedido")
            .filter(pk=pk)
            .first()
        )

    # Busca un usuario por id
    def buscar_usuario_por_id(self, pk):

        # Devuelve el usuario si existe, si no retorna None
        return Usuario.objects.filter(pk=pk).first()

    # Busca un pedido por id
    def buscar_pedido_por_id(self, pk):

        # Devuelve el pedido si existe
        return PedidoEncabezado.objects.filter(pk=pk).first()

    def pedido_ya_calificado(self, pedido_id):
        if not pedido_id:
            return False
        return CalificacionCliente.objects.filter(id_pedido_id=pedido_id).exists()

    # Busca el ultimo pedido ya finalizado de un usuario
    def buscar_ultimo_pedido_finalizado_por_usuario(self, usuario_id):
        return (
            PedidoEncabezado.objects
            .filter(id_usuario_id=usuario_id)
            .filter(estado_pedido__in=self.ESTADOS_CALIFICABLES)
            .exclude(calificacioncliente__isnull=False)
            .order_by("-id_pedido")
            .first()
        )

    # Busca el ultimo pedido finalizado aun no calificado de un usuario
    def buscar_pedido_pendiente_calificacion_por_usuario(self, usuario_id):
        return (
            PedidoEncabezado.objects
            .filter(id_usuario_id=usuario_id, estado_pedido__in=self.ESTADOS_CALIFICABLES)
            .exclude(calificacioncliente__isnull=False)
            .order_by("-id_pedido")
            .first()
        )

    # Guarda una calificación
    def guardar(self, calificacion):

        # Asegura que la tabla exista antes de guardar
        self.asegurar_tabla()

        # Evita duplicar calificaciones para el mismo pedido
        if self.pedido_ya_calificado(getattr(calificacion, "id_pedido_id", None)):
            raise ValueError("Este pedido ya fue calificado.")

        try:
            calificacion.save()
        except IntegrityError as exc:
            raise ValueError("Este pedido ya fue calificado.") from exc
        return calificacion


# Define qué se puede importar desde este archivo
__all__ = [
    "CalificacionService",
    "CalificacionCliente",
    "Usuario",
    "PedidoEncabezado"
]
