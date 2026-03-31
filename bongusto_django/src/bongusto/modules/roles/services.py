"""Servicios del modulo `roles`. 
Aqui se concentra la logica de negocio relacionada con la gestion de roles del sistema."""


# ===== Importaciones | Dependencias que este archivo necesita para funcionar dentro del modulo. =====
from bongusto.domain.models import Rol


# ===== Clase `RolService` | Modulo `roles` | Encapsula la logica de acceso y manipulacion de roles. =====
class RolService:

    # ===== Funcion `listar_todos` | Retorna todos los roles registrados en el sistema. =====
    def listar_todos(self):
        return Rol.objects.all()


    # ===== Funcion `buscar_por_id` | Busca un rol especifico por su ID. =====
    def buscar_por_id(self, pk):
        return Rol.objects.filter(pk=pk).first()


    # ===== Funcion `guardar` | Guarda o actualiza un rol en la base de datos. =====
    def guardar(self, rol):
        rol.save()
        return rol


    # ===== Funcion `eliminar` | Elimina un rol segun su ID. =====
    def eliminar(self, pk):
        Rol.objects.filter(pk=pk).delete()


# ===== Exportaciones | Define que elementos se exponen desde este modulo. =====
__all__ = ["RolService", "Rol"]
