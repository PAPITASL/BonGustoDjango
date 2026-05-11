"""
Servicios del módulo bitácora.
Aquí es donde se maneja toda la lógica relacionada con el historial de acciones.
"""
# Se importa datetime para trabajar con fechas
from datetime import datetime
# Q permite hacer filtros más completos (por ejemplo combinar condiciones)
from django.db.models import Q
# Se importa el modelo Bitacora desde la capa de dominio
from bongusto.domain.models import Bitacora
# Clase principal que contiene toda la lógica de la bitácora
class BitacoraService:
    # Trae todos los registros de la bitácora
    def listar_todas(self):
        # select_related optimiza la consulta trayendo también el usuario
        # order_by organiza los registros desde el más reciente al más antiguo
        return Bitacora.objects.select_related("id_usuario").all().order_by(
            "-fecha_accion", "-id_log"
        )
    # Lista registros aplicando filtros opcionales (usuario y/o acción)
    def listar_filtrado(self, usuario=None, accion=None):
        # Se empieza con todos los registros
        qs = self.listar_todas()
        # Si se filtra por usuario
        # Busca coincidencias en nombre o apellido
        if usuario:
            qs = qs.filter(
                Q(id_usuario__nombre__icontains=usuario) |
                Q(id_usuario__apellido__icontains=usuario)
            )
        # Si se filtra por acción
        # Busca texto dentro de la descripción de la acción
        if accion:
            qs = qs.filter(accion__icontains=accion)
        return qs
    # Busca un registro específico por su id
    def buscar_por_id(self, pk):
        # first() evita errores si no encuentra nada
        return Bitacora.objects.filter(pk=pk).first()
    # Guarda un registro (sirve tanto para crear como actualizar)
    def guardar(self, bitacora):
        # Si no tiene fecha, se le asigna automáticamente
        if not bitacora.fecha_accion:
            bitacora.fecha_accion = datetime.now()
        # Se guarda en la base de datos
        bitacora.save()
        return bitacora
    # Elimina un registro usando su id
    def eliminar(self, pk):
        # Se borra directamente desde la base de datos
        Bitacora.objects.filter(pk=pk).delete()
    # Registra una nueva acción en la bitácora
    def registrar(self, usuario, accion):
        # Se crea el registro con los datos recibidos
        entrada = Bitacora(
            id_usuario=usuario,
            accion=accion,
            fecha_accion=datetime.now()
        )
        # Se guarda en la base de datos
        entrada.save()
        return entrada
# Define qué se puede importar desde este archivo
__all__ = ["BitacoraService", "Bitacora"]