"""Vistas del perfil con un flujo corto y directo."""

from django.shortcuts import redirect, render

from bongusto.application.services import UsuarioService
from bongusto.modules.shared.audit import registrar_movimiento
from bongusto.modules.shared.security import (
    PASSWORD_POLICY_HELP,
    hash_contrasena,
    validar_contrasena_segura,
)


_service = UsuarioService()


class PerfilPageHelper:
    """Deja juntas las validaciones y contextos del perfil."""

    def usuario_actual(self, request):
        usuario_id = request.session.get("usuario_id")
        return _service.buscar_por_id(usuario_id)

    def contexto_edicion(self, usuario, error=""):
        return {
            "usuario": usuario,
            "password_policy_help": PASSWORD_POLICY_HELP,
            "error": error,
        }

    def cargar_desde_post(self, request, usuario):
        usuario.nombre = request.POST.get("nombre", usuario.nombre)
        usuario.correo = (request.POST.get("correo", usuario.correo) or "").strip().lower()
        usuario.telefono = request.POST.get("telefono", usuario.telefono)
        return usuario


_helper = PerfilPageHelper()


def ver(request):
    try:
        usuario = _helper.usuario_actual(request)
        if not usuario:
            return redirect("/login")
        return render(request, "perfil/index.html", {"usuario": usuario})
    except Exception:
        return redirect("/login")


def editar(request):
    try:
        usuario = _helper.usuario_actual(request)
        if not usuario:
            return redirect("/login")
        return render(request, "perfil/edit.html", _helper.contexto_edicion(usuario))
    except Exception:
        return redirect("/perfil")


def actualizar(request):
    if request.method != "POST":
        return redirect("/perfil")

    try:
        usuario = _helper.usuario_actual(request)
        if not usuario:
            return redirect("/login")

        usuario = _helper.cargar_desde_post(request, usuario)
        nueva_clave = (request.POST.get("nueva_clave") or "").strip()

        if nueva_clave:
            clave_valida, error_clave = validar_contrasena_segura(nueva_clave)
            if not clave_valida:
                return render(request, "perfil/edit.html", _helper.contexto_edicion(usuario, error_clave))
            usuario.clave = hash_contrasena(nueva_clave)

        _service.guardar(usuario)
        request.session["usuario_nombre"] = usuario.nombre
        registrar_movimiento(
            request,
            f"Actualizacion de perfil del usuario {usuario.nombre_completo() or usuario.correo or usuario.id_usuario}.",
        )
        return redirect("/perfil")
    except Exception:
        return redirect("/perfil")
