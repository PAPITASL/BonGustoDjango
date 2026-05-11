"""Funciones de apoyo para la autenticacion en API y WebSocket.

En este archivo se agrupan varias utilidades pequenas que ayudan
a manejar tokens, validar usuarios autenticados y controlar permisos
basicos dentro de los endpoints de la API.
"""

from functools import wraps

from django.conf import settings
from django.core import signing
from django.http import JsonResponse

from bongusto.domain.models import Usuario


API_TOKEN_SALT = "bongusto.api.token"


def api_token_ttl_seconds():
    """Devuelve el tiempo maximo de vida que tendra el token en segundos."""
    return int(getattr(settings, "API_TOKEN_TTL_SECONDS", 60 * 60 * 8))


def emitir_api_token(usuario):
    """Genera un token firmado con los datos principales del usuario autenticado."""
    payload = {
        "uid": usuario.id_usuario,
        "rol": (usuario.tipo_usuario or "").strip().lower(),
        "correo": (usuario.correo or "").strip().lower(),
    }
    return signing.dumps(payload, salt=API_TOKEN_SALT, compress=True)


def leer_api_token(token):
    """Lee el token recibido y revisa si sigue siendo valido."""
    if not token:
        raise signing.BadSignature("Token ausente")

    return signing.loads(token, salt=API_TOKEN_SALT, max_age=api_token_ttl_seconds())


def extraer_token_request(request):
    """Intenta sacar el token primero del Authorization y, si no esta, desde la URL."""
    header = (request.headers.get("Authorization", "") or "").strip()
    if header.lower().startswith("bearer "):
        return _limpiar_token(header[7:].strip())
    return _limpiar_token(request.GET.get("token") or "")


def _limpiar_token(token):
    return (token or "").strip().replace("#", "").replace("'", "").replace('"', "")


def resolver_usuario_api(request):
    """Obtiene el usuario autenticado usando el token que llega en la peticion."""
    token = extraer_token_request(request)
    if not token:
        return None, None, JsonResponse({"error": "Autenticacion requerida"}, status=401)

    try:
        payload = leer_api_token(token)
    except signing.SignatureExpired:
        return None, None, JsonResponse({"error": "La sesion expiro. Inicia sesion nuevamente."}, status=401)
    except signing.BadSignature:
        return None, None, JsonResponse({"error": "Token no valido"}, status=401)

    usuario = Usuario.objects.filter(pk=payload.get("uid"), estado__iexact="activo").first()
    if not usuario:
        return None, None, JsonResponse({"error": "Usuario no autorizado"}, status=401)

    return usuario, payload, None


def participante_permitido(usuario, participante):
    """Revisa si el usuario realmente puede actuar con ese participante dentro del chat."""
    participante = (participante or "").strip().lower()
    tipo_usuario = (usuario.tipo_usuario or "").strip().lower()

    if tipo_usuario == "cliente":
        return participante == f"cliente_{usuario.id_usuario}"
    if tipo_usuario == "mesero":
        return participante == "mesero"
    if tipo_usuario == "administrador":
        return participante == "administrador"
    return False


def api_login_required(*, roles=None):
    """Decorador que protege vistas de API usando autenticacion por token."""
    roles_set = {rol.strip().lower() for rol in (roles or []) if rol}

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Primero se busca si la peticion viene con un usuario autenticado.
            usuario, payload, error_response = resolver_usuario_api(request)
            if error_response:
                return error_response

            # Si la vista solo permite ciertos roles, aqui se valida antes de seguir.
            tipo_usuario = (usuario.tipo_usuario or "").strip().lower()
            if roles_set and tipo_usuario not in roles_set:
                return JsonResponse({"error": "No autorizado para este recurso"}, status=403)

            # Se deja el usuario guardado en el request para poder reutilizarlo dentro de la vista.
            request.api_user = usuario
            request.api_token_payload = payload
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def api_owner_or_role(request, owner_user_id, *, roles=None):
    """Permite entrar al duenio del recurso o a usuarios que tengan un rol autorizado."""
    usuario = getattr(request, "api_user", None)
    if not usuario:
        return False

    roles_set = {rol.strip().lower() for rol in (roles or []) if rol}
    tipo_usuario = (usuario.tipo_usuario or "").strip().lower()
    if tipo_usuario in roles_set:
        return True

    try:
        owner_user_id = int(owner_user_id)
    except (TypeError, ValueError):
        return False

    return usuario.id_usuario == owner_user_id


__all__ = [
    "api_login_required",
    "api_owner_or_role",
    "emitir_api_token",
    "extraer_token_request",
    "leer_api_token",
    "participante_permitido",
    "resolver_usuario_api",
]
