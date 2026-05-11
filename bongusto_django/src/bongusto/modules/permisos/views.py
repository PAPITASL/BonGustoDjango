"""Vista simple del modulo permisos."""
# Funcion para renderizar vistas
from django.shortcuts import render

# Servicio de permisos
from bongusto.application.services import PermisoService

# Instancia del servicio
_service = PermisoService()

# Vista principal de permisos
def index(request):
    try:
        # Trae todos los permisos
        permisos = _service.listar_todos()
    except Exception:
        # Si ocurre un error, deja la lista vacia
        permisos = []

    # Renderiza la vista con los datos
    return render(request, "permiso/index.html", {"permisos": permisos})