"""
Servicios del módulo bitácora.

Aquí va la lógica que maneja el historial de acciones del sistema.
"""

# Importamos datetime para manejar fechas
from datetime import datetime

# Q sirve para hacer filtros más avanzados (OR, AND, etc.)
from django.db.models import Q

# Importamos el modelo Bitacora
from bongusto.domain.models import Bitacora


# Clase principal del servicio
class BitacoraService:


    # Lista todos los registros de la bitácora
    def listar_todas(self):

        # select_related sirve para traer también el usuario sin hacer otra consulta
        # order_by ordena primero por fecha (más reciente arriba)
        return Bitacora.objects.select_related("id_usuario").all().order_by(
            "-fecha_accion", "-id_log"
        )


    # Lista con filtros (usuario y/o acción)
    def listar_filtrado(self, usuario=None, accion=None):

        # Primero trae todo
        qs = self.listar_todas()

        # Si escriben un usuario, busca por nombre o apellido
        if usuario:
            qs = qs.filter(
                Q(id_usuario__nombre__icontains=usuario) |
                Q(id_usuario__apellido__icontains=usuario)
            )

        # Si escriben una acción, filtra por texto
        if accion:
            qs = qs.filter(accion__icontains=accion)

        return qs


    # Busca un registro por id
    def buscar_por_id(self, pk):
        return Bitacora.objects.filter(pk=pk).first()


    # Guarda un registro (crear o actualizar)
    def guardar(self, bitacora):

        # Si no tiene fecha, se la asigna
        if not bitacora.fecha_accion:
            bitacora.fecha_accion = datetime.now()

        bitacora.save()
        return bitacora


    # Elimina un registro por id
    def eliminar(self, pk):
        Bitacora.objects.filter(pk=pk).delete()


    # Registra un nuevo movimiento en la bitácora
    def registrar(self, usuario, accion):

        # Se crea el registro
        entrada = Bitacora(
            id_usuario=usuario,
            accion=accion,
            fecha_accion=datetime.now()
        )

        # Se guarda en base de datos
        entrada.save()

        return entrada


# Esto define lo que se puede importar desde este archivo
__all__ = ["BitacoraService", "Bitacora"]