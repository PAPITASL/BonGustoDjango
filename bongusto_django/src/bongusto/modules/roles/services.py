"""Servicios del modulo `roles`, aqui se maneja la logica de los roles del sistema."""

# Se importa el modelo Rol
from bongusto.domain.models import Rol

# Clase donde va toda la logica de roles
class RolService:

    # Trae todos los roles
    def listar_todos(self):
        return Rol.objects.all()

    # Busca un rol por id
    def buscar_por_id(self, pk):
        return Rol.objects.filter(pk=pk).first()

    # Guarda o actualiza un rol
    def guardar(self, rol):
        rol.save()
        return rol

    # Elimina un rol por id
    def eliminar(self, pk):
        Rol.objects.filter(pk=pk).delete()

# Aqui se define lo que se exporta del servicio
__all__ = ["RolService", "Rol"]