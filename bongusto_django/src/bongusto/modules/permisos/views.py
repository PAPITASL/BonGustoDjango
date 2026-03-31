"""Vista simple del modulo permisos."""

from django.shortcuts import render

from bongusto.application.services import PermisoService


_service = PermisoService()


def index(request):
    try:
        permisos = _service.listar_todos()
    except Exception:
        permisos = []

    return render(request, "permiso/index.html", {"permisos": permisos})
