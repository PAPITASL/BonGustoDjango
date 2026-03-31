"""CRUD web de roles en un estilo simple."""

from django.shortcuts import redirect, render

from bongusto.application.services import PermisoService, RolService
from bongusto.domain.models import Rol
from bongusto.modules.shared.audit import registrar_movimiento


_service = RolService()
_permiso_service = PermisoService()


class RolPageHelper:
    """Centraliza la carga de datos del formulario."""

    def listar_roles(self):
        try:
            return _service.listar_todos()
        except Exception:
            return []

    def listar_permisos(self):
        try:
            return _permiso_service.listar_todos()
        except Exception:
            return []

    def buscar_rol(self, pk):
        try:
            return _service.buscar_por_id(pk)
        except Exception:
            return None

    def render_form(self, request, rol, accion, readonly=False, error=""):
        return render(
            request,
            "rol/form.html",
            {
                "rol": rol,
                "permisos": self.listar_permisos(),
                "accion": accion,
                "readonly": readonly,
                "error": error,
            },
        )

    def cargar_desde_post(self, request, rol):
        rol.nombre_rol = (request.POST.get("nombre_rol", "") or "").strip()
        return rol

    def validar(self, request, rol, accion):
        if not rol.nombre_rol:
            return None, self.render_form(request, rol, accion, error="Debes escribir el nombre del rol.")
        return rol, None


_helper = RolPageHelper()


def index(request):
    return render(request, "rol/index.html", {"roles": _helper.listar_roles()})


def create(request):
    return _helper.render_form(request, Rol(), "Crear")


def ver(request, pk):
    rol = _helper.buscar_rol(pk)
    if not rol:
        return redirect("/roles")
    return _helper.render_form(request, rol, "Ver", readonly=True)


def store(request):
    if request.method != "POST":
        return redirect("/roles")

    rol = _helper.cargar_desde_post(request, Rol())
    rol, error = _helper.validar(request, rol, "Crear")
    if error:
        return error

    try:
        _service.guardar(rol)
        registrar_movimiento(request, f"Creacion de rol {rol.nombre_rol or rol.id_rol}.")
        return redirect("/roles")
    except Exception:
        return _helper.render_form(request, rol, "Crear", error="No fue posible guardar el rol.")


def edit(request, pk):
    rol = _helper.buscar_rol(pk)
    if not rol:
        return redirect("/roles")
    return _helper.render_form(request, rol, "Editar")


def update(request, pk):
    if request.method != "POST":
        return redirect("/roles")

    rol = _helper.buscar_rol(pk)
    if not rol:
        return redirect("/roles")

    rol = _helper.cargar_desde_post(request, rol)
    rol, error = _helper.validar(request, rol, "Editar")
    if error:
        return error

    try:
        _service.guardar(rol)
        registrar_movimiento(request, f"Actualizacion de rol {rol.nombre_rol or rol.id_rol}.")
        return redirect("/roles")
    except Exception:
        return _helper.render_form(request, rol, "Editar", error="No fue posible actualizar el rol.")


def delete(request, pk):
    try:
        rol = _helper.buscar_rol(pk)
        _service.eliminar(pk)
        if rol:
            registrar_movimiento(request, f"Eliminacion de rol {rol.nombre_rol or rol.id_rol}.")
    except Exception:
        pass
    return redirect("/roles")
