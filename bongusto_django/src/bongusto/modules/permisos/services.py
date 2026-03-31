"""Servicios del modulo `permisos`. Aqui se maneja la logica relacionada con el catalogo de permisos del sistema."""

# ===== Importaciones | Dependencias que este archivo necesita para funcionar dentro del modulo. =====
from bongusto.domain.models import Permiso



# ===== Clase `PermisoService` | Modulo `permisos` | Agrupa la logica de negocio asociada a permisos. =====
class PermisoService:

    # ===== Funcion `listar_todos` | Modulo `permisos` | Retorna todos los permisos registrados en el sistema. =====
    def listar_todos(self):
        return Permiso.objects.all()


    # ===== Funcion `buscar_por_id` | Modulo `permisos` | Obtiene un permiso especifico por su identificador. =====
    def buscar_por_id(self, pk):
        return Permiso.objects.filter(pk=pk).first()



# ===== Exportaciones | Modulo `permisos` | Define los elementos expuestos del servicio. =====
__all__ = ["PermisoService", "Permiso"]
