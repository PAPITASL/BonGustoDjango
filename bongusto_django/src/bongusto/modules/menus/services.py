"""Servicios del modulo menus, aqui se maneja la logica principal para trabajar con los menus."""

# Importamos el modelo Menu desde la capa principal del proyecto
from bongusto.domain.models import Menu


# Clase donde se concentra toda la logica de menus
class MenuService:

    # Devuelve todos los menus registrados
    def listar_todos(self):
        return Menu.objects.all()


    # Permite filtrar menus por nombre o descripcion
    def listar_filtrado(self, nombre=None, descripcion=None):
        qs = Menu.objects.all()

        # Filtra por nombre (busqueda parcial)
        if nombre:
            qs = qs.filter(nombre_menu__icontains=nombre)

        # Filtra por descripcion (busqueda parcial)
        if descripcion:
            qs = qs.filter(descripcion_menu__icontains=descripcion)

        return qs


    # Busca un menu especifico por su id
    def buscar_por_id(self, pk):
        return Menu.objects.filter(pk=pk).first()


    # Guarda un menu (sirve tanto para crear como actualizar)
    def guardar(self, menu):
        menu.save()
        return menu


    # Elimina un menu usando su id
    def eliminar(self, pk):
        from bongusto.domain.models import Producto

        menu = Menu.objects.filter(pk=pk).first()
        if not menu:
            return

        if Producto.objects.filter(id_menu=menu).exists():
            raise ValueError("No se puede eliminar este menu porque tiene productos asociados.")

        menu.delete()


# Define que se puede importar desde este archivo
__all__ = ["MenuService", "Menu"]
