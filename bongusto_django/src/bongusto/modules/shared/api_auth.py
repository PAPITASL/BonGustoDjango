"""Utilidades de autenticacion para APIs y WebSocket.

Este archivo concentra funciones pequenas relacionadas con tokens,
usuarios autenticados y permisos basicos para endpoints de la API.
"""

from functools import wraps

from django.conf import settings
from django.core import signing
from django.http import JsonResponse

from bongusto.domain.models import Usuario


API_TOKEN_SALT = "bongusto.api.token"


def api_token_ttl_seconds():
    """Retorna la duracion maxima del token en segundos."""
    return int(getattr(settings, "API_TOKEN_TTL_SECONDS", 60 * 60 * 8))


def emitir_api_token(usuario):
    """Crea un token firmado para el usuario autenticado."""
    payload = {
        "uid": usuario.id_usuario,
        "rol": (usuario.tipo_usuario or "").strip().lower(),
        "correo": (usuario.correo or "").strip().lower(),
    }
    return signing.dumps(payload, salt=API_TOKEN_SALT, compress=True)


def leer_api_token(token):
    """Lee y valida un token firmado recibido desde el cliente."""
    if not token:
        raise signing.BadSignature("Token ausente")

    return signing.loads(token, salt=API_TOKEN_SALT, max_age=api_token_ttl_seconds())


def extraer_token_request(request):
    """Busca el token primero en Authorization y luego en query params."""
    header = (request.headers.get("Authorization", "") or "").strip()
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return (request.GET.get("token") or "").strip()


def resolver_usuario_api(request):
    """Resuelve el usuario autenticado a partir del token recibido."""
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
    """Valida si un usuario puede actuar como cierto participante del chat."""
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
    """Decorador para proteger vistas de API con autenticacion por token."""
    roles_set = {rol.strip().lower() for rol in (roles or []) if rol}

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Primero se intenta identificar al usuario autenticado.
            usuario, payload, error_response = resolver_usuario_api(request)
            if error_response:
                return error_response

            # Si la vista exige ciertos roles, se valida antes de continuar.
            tipo_usuario = (usuario.tipo_usuario or "").strip().lower()
            if roles_set and tipo_usuario not in roles_set:
                return JsonResponse({"error": "No autorizado para este recurso"}, status=403)

            # Se guarda el usuario en el request para reutilizarlo en la vista.
            request.api_user = usuario
            request.api_token_payload = payload
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def api_owner_or_role(request, owner_user_id, *, roles=None):
    """Permite acceso al dueño del recurso o a un rol autorizado."""
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
