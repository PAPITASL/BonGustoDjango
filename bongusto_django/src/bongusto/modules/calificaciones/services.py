"""
Servicios del módulo calificaciones.

Aquí se maneja toda la lógica de opiniones y puntajes de clientes.
"""

# Permite ejecutar SQL directamente
from django.db import connection

# Para filtros más avanzados
from django.db.models import Q

# Modelos
from bongusto.domain.models import CalificacionCliente, PedidoEncabezado, Usuario


class CalificacionService:


    # Asegura que la tabla exista en la base de datos
    def asegurar_tabla(self):

        # cursor sirve para ejecutar SQL manual
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


    # Lista todas las calificaciones
    def listar_todas(self):

        # Primero se asegura que la tabla exista
        self.asegurar_tabla()

        # select_related trae usuario y pedido en una sola consulta (optimiza)
        return (
            CalificacionCliente.objects
            .select_related("id_usuario", "id_pedido")
            .all()
            .order_by("-fecha_calificacion", "-id_calificacion")
        )


    # Lista con filtros
    def listar_filtrado(self, usuario=None, puntaje=None):

        qs = self.listar_todas()

        # Filtro por nombre o apellido del usuario
        if usuario:
            qs = qs.filter(
                Q(id_usuario__nombre__icontains=usuario) |
                Q(id_usuario__apellido__icontains=usuario)
            )

        # Filtro por puntaje mínimo
        if puntaje:
            try:
                puntaje_int = int(puntaje)
            except (TypeError, ValueError):
                puntaje_int = None

            # Aquí se usa una lista porque promedio es un cálculo (no está en DB)
            if puntaje_int:
                qs = [
                    item for item in qs
                    if int(item.promedio or 0) >= puntaje_int
                ]

        return qs


    # Buscar una calificación por id
    def buscar_por_id(self, pk):

        self.asegurar_tabla()

        return (
            CalificacionCliente.objects
            .select_related("id_usuario", "id_pedido")
            .filter(pk=pk)
            .first()
        )


    # Buscar usuario por id
    def buscar_usuario_por_id(self, pk):
        return Usuario.objects.filter(pk=pk).first()


    # Buscar pedido por id
    def buscar_pedido_por_id(self, pk):
        return PedidoEncabezado.objects.filter(pk=pk).first()


    # Guardar calificación
    def guardar(self, calificacion):

        self.asegurar_tabla()

        calificacion.save()
        return calificacion


# Define lo que se exporta desde este archivo
__all__ = [
    "CalificacionService",
    "CalificacionCliente",
    "Usuario",
    "PedidoEncabezado"
]