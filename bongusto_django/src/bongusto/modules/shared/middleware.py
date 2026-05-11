"""Middleware encargado de validar la autenticacion por sesion."""

from django.shortcuts import redirect


# Rutas que NO requieren autenticacion.
# Todo lo que empiece por estas rutas puede entrar sin haber iniciado sesion.
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
    """Se encarga de proteger las rutas privadas cuando no hay un usuario en sesion."""

    def __init__(self, get_response):
        # Django pasa automaticamente la funcion que continua el flujo de la peticion.
        self.get_response = get_response

    def __call__(self, request):
        # Se obtiene la ruta actual que el usuario esta intentando acceder.
        path = request.path

        # Se valida si la ruta es publica (es decir, no necesita login).
        es_publica = path == "/" or any(path.startswith(ruta) for ruta in RUTAS_PUBLICAS)

        # Se revisa si existe un usuario guardado en la sesion.
        usuario_en_sesion = request.session.get("usuario_id")

        # Regla principal del middleware:
        # Si la ruta NO es publica y NO hay usuario autenticado,
        # entonces se bloquea el acceso y se envia al login.
        if not es_publica and not usuario_en_sesion:
            return redirect("/login")

        # Si todo esta correcto, la peticion sigue su flujo normal hacia la vista.
        return self.get_response(request)


# Se define lo que este modulo expone cuando es importado en otras partes del sistema.
__all__ = ["AuthMiddleware", "RUTAS_PUBLICAS"]
