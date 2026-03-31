"""Servicios del modulo menus, aqui se maneja la logica principal para la gestion de menus."""

# ===== Importacion principal | Se usa el modelo Menu desde la capa de dominio. =====
from bongusto.domain.models import Menu


# ===== Clase principal de menus | Aqui se concentra toda la logica relacionada con menus. =====
class MenuService:

    # Listar todos los menus
    def listar_todos(self):
        return Menu.objects.all()


    # Listar con filtros por nombre y descripcion
    def listar_filtrado(self, nombre=None, descripcion=None):
        qs = Menu.objects.all()

        if nombre:
            qs = qs.filter(nombre_menu__icontains=nombre)

        if descripcion:
            qs = qs.filter(descripcion_menu__icontains=descripcion)

        return qs


    # Buscar un menu por su id
    def buscar_por_id(self, pk):
        return Menu.objects.filter(pk=pk).first()


    # Guardar o actualizar un menu
    def guardar(self, menu):
        menu.save()
        return menu


    # Eliminar un menu por id
    def eliminar(self, pk):
        Menu.objects.filter(pk=pk).delete()


# ===== Exportacion del servicio =====
__all__ = ["MenuService", "Menu"]
