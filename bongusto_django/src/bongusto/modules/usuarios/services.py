"""Servicios del modulo `usuarios`. Aqui se concentra la logica de negocio relacionada con usuarios del sistema y clientes API."""


# ===== Importaciones | Modelos del dominio y utilidades de seguridad. =====
from bongusto.domain.models import Bitacora, Reserva, Rol, Usuario
from bongusto.modules.shared.security import verificar_contrasena_usuario


# ===== Clase `UsuarioService` | Modulo `usuarios` | Centraliza toda la logica de usuarios (CRUD + autenticacion). =====
class UsuarioService:
    """Gestion de usuarios: CRUD + filtros."""


    # ===== Funcion `listar_todos` | Retorna todos los usuarios con su rol asociado. =====
    def listar_todos(self):
        return Usuario.objects.select_related("id_rol").all()


    # ===== Funcion `listar_filtrado` | Permite buscar usuarios segun filtros dinamicos. =====
    def listar_filtrado(self, nombre=None, correo=None, rol=None, estado=None):
        qs = self.listar_todos()

        # Filtro por nombre (busqueda parcial)
        if nombre:
            qs = qs.filter(nombre__icontains=nombre)

        # Filtro por correo
        if correo:
            qs = qs.filter(correo__icontains=correo)

        # Filtro por nombre del rol
        if rol:
            qs = qs.filter(id_rol__nombre_rol__icontains=rol)

        # Filtro por estado exacto (Activo / Inactivo)
        if estado:
            qs = qs.filter(estado__iexact=estado)

        return qs


    # ===== Funcion `buscar_por_id` | Busca un usuario especifico por su ID. =====
    def buscar_por_id(self, pk):
        return Usuario.objects.select_related("id_rol").filter(pk=pk).first()


    # ===== Funcion `buscar_por_correo` | Busca un usuario usando su correo (login). =====
    def buscar_por_correo(self, correo):
        return Usuario.objects.filter(correo__iexact=correo).first()


    # ===== Funcion `guardar` | Guarda o actualiza un usuario en base de datos. =====
    def guardar(self, usuario):
        usuario.save()
        return usuario


    # ===== Funcion `eliminar` | Elimina un usuario por su ID. =====
    def eliminar(self, pk):
        Usuario.objects.filter(pk=pk).delete()


    # ===== Funcion `autenticar` | Valida credenciales del usuario usando hash seguro. =====
    def autenticar(self, correo, clave):
        usuario = self.buscar_por_correo(correo)

        # Verifica que exista y que la contrasena sea valida
        if usuario and verificar_contrasena_usuario(usuario, clave):
            return usuario

        return None


# ===== Exportaciones | Elementos disponibles para otros modulos. =====
__all__ = ["UsuarioService", "Usuario", "Rol", "Reserva", "Bitacora"]