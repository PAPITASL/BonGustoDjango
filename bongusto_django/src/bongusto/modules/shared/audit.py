"""Funciones compartidas para registrar acciones en bitacora."""

from bongusto.application.services import BitacoraService, UsuarioService


_bitacora_service = BitacoraService()
_usuario_service = UsuarioService()


def usuario_actual(request):
    session = getattr(request, "session", None)
    usuario_id = session.get("usuario_id") if session else None

    if not usuario_id:
        return None

    try:
        return _usuario_service.buscar_por_id(usuario_id)
    except Exception:
        return None


def registrar_movimiento(request, accion):
    try:
        usuario = usuario_actual(request)
        _bitacora_service.registrar(usuario, accion)
    except Exception:
        return None


__all__ = ["registrar_movimiento", "usuario_actual"]
