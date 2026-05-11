"""Servicios del modulo `productos`, aqui se maneja la logica de los productos del restaurante."""

# Se importan los modelos que se van a usar
from bongusto.domain.models import Categoria, Menu, Producto

# Clase donde va toda la logica de productos
class ProductoService:

    # Trae todos los productos con su menu y categoria
    def listar_todos(self):
        return Producto.objects.select_related("id_menu", "id_cate").all()

    # Permite filtrar productos por varios campos
    def listar_filtrado(self, nombre=None, categoria=None, menu=None, precio_min=None, precio_max=None):
        qs = self.listar_todos()

        # Filtra por nombre
        if nombre:
            qs = qs.filter(nombre_producto__icontains=nombre)

        # Filtra por categoria
        if categoria:
            qs = qs.filter(id_cate__nombre_cate__icontains=categoria)

        # Filtra por menu
        if menu:
            qs = qs.filter(id_menu__nombre_menu__icontains=menu)

        # Filtra por precio minimo
        if precio_min not in (None, ""):
            qs = qs.filter(precio_producto__gte=precio_min)

        # Filtra por precio maximo
        if precio_max not in (None, ""):
            qs = qs.filter(precio_producto__lte=precio_max)

        return qs

    # Busca un producto por id
    def buscar_por_id(self, pk):
        return Producto.objects.select_related("id_menu", "id_cate").filter(pk=pk).first()

    # Guarda un producto en la base de datos
    def guardar(self, producto):
        producto.save()
        return producto

    # Elimina un producto por id
    def eliminar(self, pk):
        Producto.objects.filter(pk=pk).delete()

# Aqui se define lo que se exporta del servicio
__all__ = ["ProductoService", "Producto", "Menu", "Categoria"]