"""Servicios del modulo `permisos`, aqui se maneja la logica de los permisos del sistema."""

# Se importa el modelo Permiso
from bongusto.domain.models import Permiso

# Clase donde va la logica de permisos
class PermisoService:

    # Trae todos los permisos
    def listar_todos(self):
        return Permiso.objects.all()

    # Busca un permiso por id
    def buscar_por_id(self, pk):
        return Permiso.objects.filter(pk=pk).first()

# Aqui se define lo que se exporta del servicio
__all__ = ["PermisoService", "Permiso"]