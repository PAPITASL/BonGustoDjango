"""Servicios del modulo `productos`. Aqui se maneja la logica relacionada con platos y productos del restaurante."""

# ===== Importaciones | Dependencias que este archivo necesita para funcionar dentro del modulo. =====
from bongusto.domain.models import Categoria, Menu, Producto



# ===== Clase `ProductoService` | Modulo `productos` | Agrupa la logica de negocio asociada a productos. =====
class ProductoService:

    # ===== Funcion `listar_todos` | Modulo `productos` | Retorna todos los productos con sus relaciones principales. =====
    def listar_todos(self):
        return Producto.objects.select_related("id_menu", "id_cate").all()


    # ===== Funcion `listar_filtrado` | Modulo `productos` | Permite filtrar productos por nombre, categoria, menu y rango de precios. =====
    def listar_filtrado(self, nombre=None, categoria=None, menu=None, precio_min=None, precio_max=None):
        qs = self.listar_todos()

        if nombre:
            qs = qs.filter(nombre_producto__icontains=nombre)

        if categoria:
            qs = qs.filter(id_cate__nombre_cate__icontains=categoria)

        if menu:
            qs = qs.filter(id_menu__nombre_menu__icontains=menu)

        if precio_min not in (None, ""):
            qs = qs.filter(precio_producto__gte=precio_min)

        if precio_max not in (None, ""):
            qs = qs.filter(precio_producto__lte=precio_max)

        return qs


    # ===== Funcion `buscar_por_id` | Modulo `productos` | Obtiene un producto especifico junto a sus relaciones. =====
    def buscar_por_id(self, pk):
        return Producto.objects.select_related("id_menu", "id_cate").filter(pk=pk).first()


    # ===== Funcion `guardar` | Modulo `productos` | Persiste un producto en la base de datos. =====
    def guardar(self, producto):
        producto.save()
        return producto


    # ===== Funcion `eliminar` | Modulo `productos` | Elimina un producto por su identificador. =====
    def eliminar(self, pk):
        Producto.objects.filter(pk=pk).delete()



# ===== Exportaciones | Modulo `productos` | Define los elementos disponibles para otras capas. =====
__all__ = ["ProductoService", "Producto", "Menu", "Categoria"]