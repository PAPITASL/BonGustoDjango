"""Funciones compartidas para registrar acciones dentro de la bitacora del sistema."""

from bongusto.application.services import BitacoraService, UsuarioService
from bongusto.domain.models import Usuario


_bitacora_service = BitacoraService()
_usuario_service = UsuarioService()


def usuario_actual(request):
    """Intenta obtener el usuario actual desde API o sesion web."""
    api_user = getattr(request, "api_user", None)
    if isinstance(api_user, Usuario):
        return api_user

    api_user_id = getattr(api_user, "id_usuario", None)
    if api_user_id:
        try:
            return _usuario_service.buscar_por_id(api_user_id)
        except Exception:
            pass

    session = getattr(request, "session", None)
    usuario_id = session.get("usuario_id") if session else None

    if not usuario_id:
        return None

    try:
        return _usuario_service.buscar_por_id(usuario_id)
    except Exception:
        return None


def registrar_movimiento(request, accion):
    """Registra una accion en la bitacora asociada al usuario actual."""
    try:
        usuario = usuario_actual(request)
        _bitacora_service.registrar(usuario, accion)
    except Exception:
        return None


__all__ = ["registrar_movimiento", "usuario_actual"]
