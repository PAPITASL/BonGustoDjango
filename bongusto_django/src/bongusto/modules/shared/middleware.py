"""Middleware de autenticacion por sesion."""

from django.shortcuts import redirect


RUTAS_PUBLICAS = (
    "/login",
    "/logout",
    "/healthz",
    "/password/",
    "/api/",
    "/static/",
    "/favicon.ico",
)


class AuthMiddleware:
    """Protege rutas privadas cuando no hay sesion activa."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        es_publica = any(path.startswith(ruta) for ruta in RUTAS_PUBLICAS)
        usuario_en_sesion = request.session.get("usuario_id")

        if not es_publica and not usuario_en_sesion:
            return redirect("/login")

        return self.get_response(request)


__all__ = ["AuthMiddleware", "RUTAS_PUBLICAS"]
