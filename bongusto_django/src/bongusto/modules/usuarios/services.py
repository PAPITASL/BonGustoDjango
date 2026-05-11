"""Servicios del modulo `usuarios`.
Aqui se centraliza toda la logica de negocio relacionada con los usuarios
del sistema, incluyendo operaciones CRUD y procesos de autenticacion.
"""
# ===== Importaciones | Se traen los modelos necesarios y funciones de seguridad. =====
from bongusto.domain.models import Bitacora, Reserva, Rol, Usuario
from bongusto.modules.shared.security import verificar_contrasena_usuario

# ===== Clase `UsuarioService` | Modulo `usuarios` | Encapsula toda la logica de usuarios. =====
class UsuarioService:
    """Gestion de usuarios: CRUD + filtros + autenticacion."""

    # ===== Funcion `usuario_activo` | Valida si el usuario puede entrar al sistema. =====
    def usuario_activo(self, usuario):
        estado = (getattr(usuario, "estado", "") or "").strip().lower()
        return estado == "activo"

    # ===== Funcion `listar_todos` | Devuelve todos los usuarios con su rol cargado. =====
    def listar_todos(self):
        # select_related evita consultas extra al traer el rol en la misma consulta
        return Usuario.objects.select_related("id_rol").all()

    # ===== Funcion `listar_filtrado` | Permite aplicar filtros dinamicos segun los parametros. =====
    def listar_filtrado(self, nombre=None, correo=None, rol=None, estado=None):
        # Se parte del queryset base
        qs = self.listar_todos()

        # Filtro por nombre (busqueda parcial, no exacta)
        if nombre:
            qs = qs.filter(nombre__icontains=nombre)

        # Filtro por correo (tambien parcial)
        if correo:
            qs = qs.filter(correo__icontains=correo)

        # Filtro por nombre del rol (relacion con tabla Rol)
        if rol:
            qs = qs.filter(id_rol__nombre_rol__icontains=rol)

        # Filtro por estado (Activo / Inactivo, sin importar mayusculas)
        if estado:
            qs = qs.filter(estado__iexact=estado)

        return qs

    # ===== Funcion `buscar_por_id` | Retorna un usuario especifico segun su ID. =====
    def buscar_por_id(self, pk):
        # first() evita errores si no existe el usuario
        return Usuario.objects.select_related("id_rol").filter(pk=pk).first()

    # ===== Funcion `buscar_por_correo` | Usada principalmente en login. =====
    def buscar_por_correo(self, correo):
        # iexact permite comparar sin importar mayusculas/minusculas
        return Usuario.objects.filter(correo__iexact=correo).first()

    # ===== Funcion `guardar` | Guarda o actualiza un usuario en la base de datos. =====
    def guardar(self, usuario):
        # save() funciona tanto para crear como para actualizar
        usuario.save()
        return usuario

    # ===== Funcion `eliminar` | Elimina un usuario por su ID. =====
    def eliminar(self, pk):
        # Se usa filter + delete para evitar errores si no existe
        Usuario.objects.filter(pk=pk).delete()

    # ===== Funcion `autenticar` | Valida credenciales usando seguridad del sistema. =====
    def autenticar(self, correo, clave):
        # Se busca el usuario por su correo
        usuario = self.buscar_por_correo(correo)

        # Se valida que exista y que la contrasena coincida (con hash seguro)
        if usuario and self.usuario_activo(usuario) and verificar_contrasena_usuario(usuario, clave):
            return usuario

        # Si falla cualquiera de las dos, no se autentica
        return None

# ===== Exportaciones | Define lo que otros modulos pueden importar desde aqui. =====
__all__ = ["UsuarioService", "Usuario", "Rol", "Reserva", "Bitacora"]
