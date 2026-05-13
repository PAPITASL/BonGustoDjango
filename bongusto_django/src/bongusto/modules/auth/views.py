"""Vistas del módulo de autenticación con un flujo claro y fácil de entender."""

from datetime import datetime, timedelta
from email.mime.image import MIMEImage
from pathlib import Path
from secrets import randbelow
from django.conf import settings
from django.core.cache import cache
from django.core import signing
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from bongusto.application.services import UsuarioService
from bongusto.domain.models import Usuario
from bongusto.modules.shared.audit import registrar_movimiento
from bongusto.modules.shared.security import (
    PASSWORD_POLICY_HELP,
    hash_contrasena,
    validar_contrasena_segura,
)

# Se crea una instancia del servicio de usuario.
# Desde aquí se apoya toda la parte lógica del login.
_service = UsuarioService()


class AuthPageHelper:
    """Aquí se agrupan varias ayudas para no repetir lógica y dejar las vistas más ordenadas."""

    # Arma el contexto básico del login.
    # Si llega un error, se manda al template.
    def contexto_login(self, error=""):
        return {"error": error} if error else {}

    # Arma el contexto para la vista donde el usuario escribe su correo.
    def contexto_email(self, email="", error="", success=""):
        return {"email": email, "error": error, "success_message": success}

    def mensaje_error_envio(self, exc):
        if settings.DEBUG and exc:
            return f"No fue posible enviar el codigo de recuperacion en este momento. Detalle: {exc}"
        return "No fue posible enviar el codigo de recuperacion en este momento."

    # Arma el contexto para la vista de cambio de contraseña.
    # También manda la ayuda de la política de seguridad.
    def contexto_reset(self, email="", error="", success="", code=""):
        return {
            "email": email,
            "error": error,
            "success_message": success,
            "code": code,
            "password_policy_help": PASSWORD_POLICY_HELP,
        }

    # Crea los datos temporales para la recuperación.
    # Guarda correo, código y fecha de vencimiento.
    def crear_sesion_recuperacion(self, email, code):
        vence = timezone.now() + timedelta(minutes=settings.PASSWORD_RESET_CODE_TTL_MINUTES)
        return {
            "email": email,
            "code": code,
            "expires_at": vence.isoformat(),
        }

    # Valida que la información temporal del reset siga siendo válida.
    # Revisa que exista, que correo y código coincidan y que todavía no haya vencido.
    def validar_sesion_recuperacion(self, reset_data, email, code):
        if not reset_data:
            return False, "Primero solicita el codigo de recuperacion."

        if (reset_data.get("email") or "").strip().lower() != email:
            return False, "El correo no coincide con la solicitud de recuperacion."

        if (reset_data.get("code") or "").strip() != code:
            return False, "El codigo de verificacion no es valido."

        expires_at_raw = reset_data.get("expires_at") or ""
        try:
            expires_at = datetime.fromisoformat(expires_at_raw)

            # Si la fecha viene sin zona horaria, se ajusta a la zona actual del sistema.
            if timezone.is_naive(expires_at):
                expires_at = timezone.make_aware(expires_at, timezone.get_current_timezone())
        except ValueError:
            return False, "La solicitud de recuperacion no es valida."

        if timezone.now() > expires_at:
            return False, "El codigo de verificacion ya vencio. Solicita uno nuevo."

        return True, ""

    def cache_key_recuperacion(self, email):
        return f"password_reset:{(email or '').strip().lower()}"

    def guardar_codigo_api(self, email, code):
        cache.set(
            self.cache_key_recuperacion(email),
            self.crear_sesion_recuperacion(email, code),
            timeout=settings.PASSWORD_RESET_CODE_TTL_MINUTES * 60,
        )

    def leer_codigo_api(self, email):
        return cache.get(self.cache_key_recuperacion(email))

    def limpiar_codigo_api(self, email):
        cache.delete(self.cache_key_recuperacion(email))

    # Busca un usuario usando el correo sin importar mayúsculas o minúsculas.
    def buscar_usuario_por_correo(self, email):
        return Usuario.objects.filter(correo__iexact=email).first()

    # Usa el servicio para autenticar al usuario con correo y clave.
    def autenticar(self, correo, clave):
        return _service.autenticar(correo, clave)

    # Guarda en sesión los datos más importantes cuando el usuario inicia sesión.
    def guardar_sesion_login(self, request, usuario):
        request.session.cycle_key()
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre
        request.session["usuario_tipo"] = usuario.tipo_usuario
        request.session.set_expiry(3600)

    # Genera un código aleatorio de 6 números para recuperación.
    def codigo_recuperacion(self):
        return f"{randbelow(1_000_000):06d}"

    # Verifica si el correo del sistema está listo para enviar mensajes.
    def correo_configurado(self):
        backend = (getattr(settings, "EMAIL_BACKEND", "") or "").strip()
        if backend != "django.core.mail.backends.smtp.EmailBackend":
            return True

        return all(
            [
                (getattr(settings, "EMAIL_HOST", "") or "").strip(),
                str(getattr(settings, "EMAIL_PORT", "") or "").strip(),
                (getattr(settings, "EMAIL_HOST_USER", "") or "").strip(),
                (getattr(settings, "EMAIL_HOST_PASSWORD", "") or "").strip(),
            ]
        )

    # Construye el contexto que se manda al correo en texto y en HTML.
    def construir_contexto_correo(self, usuario, code):
        return {
            "nombre_usuario": usuario.nombre_completo() or usuario.correo or "usuario",
            "code": code,
            "ttl_minutes": settings.PASSWORD_RESET_CODE_TTL_MINUTES,
            "support_email": settings.DEFAULT_FROM_EMAIL,
        }

    def generar_token_recuperacion(self, usuario_id):
        return signing.dumps({"usuario_id": usuario_id}, salt="bongusto.password_reset")

    def validar_token_recuperacion(self, token):
        try:
            data = signing.loads(
                token,
                salt="bongusto.password_reset",
                max_age=settings.PASSWORD_RESET_TOKEN_TTL_SECONDS,
            )
            return int(data.get("usuario_id")), None
        except Exception:
            return None, "El enlace de recuperacion no es valido o ya vencio."

    def guardar_token_api(self, email, token):
        cache.set(
            self.cache_key_recuperacion(f"token:{token}"),
            {
                "email": email,
                "token": token,
                "expires_at": (timezone.now() + timedelta(seconds=settings.PASSWORD_RESET_TOKEN_TTL_SECONDS)).isoformat(),
            },
            timeout=settings.PASSWORD_RESET_TOKEN_TTL_SECONDS,
        )

    def leer_token_api(self, token):
        return cache.get(self.cache_key_recuperacion(f"token:{token}"))

    def limpiar_token_api(self, token):
        cache.delete(self.cache_key_recuperacion(f"token:{token}"))

    def construir_contexto_enlace(self, usuario, reset_url):
        return {
            "nombre_usuario": usuario.nombre_completo() or usuario.correo or "usuario",
            "reset_url": reset_url,
            "ttl_minutes": max(1, settings.PASSWORD_RESET_TOKEN_TTL_SECONDS // 60),
            "support_email": settings.DEFAULT_FROM_EMAIL,
        }

    # Devuelve la ruta donde está guardado el logo que se adjunta al correo.
    def logo_path(self):
        return (
            Path(settings.BASE_DIR)
            / "src"
            / "bongusto"
            / "modules"
            / "shared"
            / "static"
            / "img"
            / "logobongusto.png"
        )

    # Arma y envía el correo de recuperación.
    # Manda versión texto, versión HTML y agrega el logo si existe.
    def enviar_correo_recuperacion(self, email, context):
        text_body = render_to_string("auth/password_reset_email.txt", context)
        html_body = render_to_string("auth/password_reset_email.html", context)

        message = EmailMultiAlternatives(
            subject="BonGusto | Codigo de recuperacion de acceso",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        message.attach_alternative(html_body, "text/html")
        logo_path = self.logo_path()
        if logo_path.exists():
            with logo_path.open("rb") as logo_file:
                logo = MIMEImage(logo_file.read())
                logo.add_header("Content-ID", "<bongusto-logo>")
                logo.add_header("Content-Disposition", "inline", filename="logobongusto.png")
                message.attach(logo)
        message.send(fail_silently=False)

    def enviar_correo_enlace_recuperacion(self, email, context):
        text_body = render_to_string("auth/password_reset_link_email.txt", context)
        html_body = render_to_string("auth/password_reset_link_email.html", context)

        message = EmailMultiAlternatives(
            subject="Recuperacion de contrasena - BonGusto",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        message.attach_alternative(html_body, "text/html")
        logo_path = self.logo_path()
        if logo_path.exists():
            with logo_path.open("rb") as logo_file:
                logo = MIMEImage(logo_file.read())
                logo.add_header("Content-ID", "<bongusto-logo>")
                logo.add_header("Content-Disposition", "inline", filename="logobongusto.png")
                message.attach(logo)
        message.send(fail_silently=False)

    def construir_url_recuperacion(self, request, token):
        if request is not None:
            return request.build_absolute_uri(f"/restablecer-password/?token={token}")
        return f"http://127.0.0.1:8000/restablecer-password/?token={token}"


# Se crea una instancia del helper para reutilizar toda esta ayuda.
_helper = AuthPageHelper()


# Esta vista manda la raíz directamente al login.
def redirect_root(request):
    return redirect("/login")


# Vista principal de inicio de sesión.
def login_view(request):
    # Si entra por GET, solo muestra la pantalla del login.
    if request.method != "POST":
        return render(request, "auth/login.html")
    try:
        # Se capturan los datos enviados desde el formulario.
        correo = (request.POST.get("username", "") or "").strip().lower()
        clave = request.POST.get("password", "")

        # Se intenta autenticar al usuario con esos datos.
        usuario = _helper.autenticar(correo, clave)

        if not usuario:
            usuario_inactivo = _helper.buscar_usuario_por_correo(correo)
            if usuario_inactivo and (usuario_inactivo.estado or "").strip().lower() != "activo":
                return render(
                    request,
                    "auth/login.html",
                    _helper.contexto_login("Esta cuenta esta desactivada. Contacta al administrador."),
                )

        # Si no encuentra usuario o la clave falla, muestra mensaje de error.
        if not usuario:
            return render(request, "auth/login.html", _helper.contexto_login("Correo o contrasena incorrectos"))

        # Si todo sale bien, guarda la sesión del usuario.
        _helper.guardar_sesion_login(request, usuario)

        # Registra en bitácora el inicio de sesión.
        registrar_movimiento(
            request,
            f"Inicio de sesion del usuario {usuario.nombre_completo() or usuario.correo or usuario.id_usuario}.",
        )

        # Luego lo manda al dashboard.
        return redirect("/dashboard")
    except Exception:
        # Si algo falla en el proceso, muestra un error general.
        return render(
            request,
            "auth/login.html",
            _helper.contexto_login("No fue posible iniciar sesion en este momento."),
        )


# Vista para cerrar sesión.
# never_cache evita comportamientos raros por caché del navegador.
@never_cache
def logout_view(request):
    try:
        # Guarda el nombre antes de limpiar la sesión.
        usuario_nombre = request.session.get("usuario_nombre", "Usuario")

        # Se registra el cierre de sesión en bitácora.
        registrar_movimiento(request, f"Cierre de sesion del usuario {usuario_nombre}.")

        # Se borra completamente la sesión actual.
        request.session.flush()

        # Se renderiza la pantalla de cierre de sesión.
        response = render(request, "auth/logout.html")

        # Cabeceras para evitar que el navegador guarde esta respuesta en caché.
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        return response
    except Exception:
        # Si pasa algo inesperado, igual limpia la sesión y devuelve al login.
        request.session.flush()
        return redirect("/login")


# Vista donde el usuario pide el correo de recuperación.
def password_email(request):
    # Si entra por GET, solo carga la vista.
    if request.method == "GET":
        return render(request, "auth/email.html")

    # Se toma el correo escrito por el usuario.
    email = (request.POST.get("email", "") or "").strip().lower()
    try:
        # Se busca si existe un usuario con ese correo.
        usuario = _helper.buscar_usuario_por_correo(email)
        if not usuario:
            return render(
                request,
                "auth/email.html",
                _helper.contexto_email(email, "No existe un usuario asociado a ese correo."),
            )

        # Se genera y guarda un codigo temporal para validar el cambio.
        code = _helper.codigo_recuperacion()
        request.session["password_reset"] = _helper.crear_sesion_recuperacion(email, code)
        _helper.guardar_codigo_api(email, code)

        # Si el modo demo está activo o el correo no está configurado,
        # se muestra el codigo directamente para pruebas locales.
        if settings.DEMO_MODE or not _helper.correo_configurado():
            registrar_movimiento(
                request,
                f"Solicitud de recuperacion por codigo preparada en modo demo para {email}.",
            )
            return render(
                request,
                "auth/reset_password.html",
                _helper.contexto_reset(
                    email,
                    success="Se genero un codigo de recuperacion. Revisa el mensaje de prueba e ingresalo para cambiar la contrasena.",
                    code=code,
                ),
            )

        # Arma el contexto del correo y lo envía.
        contexto = _helper.construir_contexto_correo(usuario, code)
        _helper.enviar_correo_recuperacion(email, contexto)

        # Lleva de una vez al formulario para ingresar el codigo y la nueva clave.
        return render(
            request,
            "auth/reset_password.html",
            _helper.contexto_reset(
                email,
                success="Te enviamos un codigo de recuperacion al correo registrado.",
            ),
        )
    except Exception as exc:
        # Si algo falla, se muestra un mensaje general.
        return render(
            request,
            "auth/email.html",
            _helper.contexto_email(
                email,
                _helper.mensaje_error_envio(exc),
            ),
        )


# Vista para restablecer la contraseña.
def password_reset(request):
    email = request.GET.get("email", "")

    # Si entra por GET, solo muestra el formulario.
    if request.method != "POST":
        return render(request, "auth/reset_password.html", _helper.contexto_reset(email))
    try:
        # Se recogen todos los datos enviados en el formulario.
        email = (request.POST.get("email", "") or "").strip().lower()
        code = (request.POST.get("code", "") or "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        # Se trae la información temporal guardada en sesión.
        reset_data = request.session.get("password_reset")

        # Se valida que la solicitud de recuperación siga siendo válida.
        codigo_valido, error = _helper.validar_sesion_recuperacion(reset_data, email, code)
        if not codigo_valido:
            return render(request, "auth/reset_password.html", _helper.contexto_reset(email, error))

        # Se revisa que ambas contraseñas coincidan.
        if password != password_confirm:
            return render(
                request,
                "auth/reset_password.html",
                _helper.contexto_reset(email, "Las contrasenas no coinciden."),
            )

        # Se valida que la nueva contraseña cumpla la política de seguridad.
        clave_valida, error_clave = validar_contrasena_segura(password)
        if not clave_valida:
            return render(request, "auth/reset_password.html", _helper.contexto_reset(email, error_clave))

        # Se vuelve a buscar el usuario por correo.
        usuario = _helper.buscar_usuario_por_correo(email)
        if not usuario:
            return render(
                request,
                "auth/reset_password.html",
                _helper.contexto_reset(email, "No existe un usuario asociado a ese correo."),
            )

        # Se guarda la nueva contraseña ya cifrada.
        usuario.clave = hash_contrasena(password)
        usuario.save(update_fields=["clave"])

        # Se limpia la sesión temporal del proceso de recuperación.
        request.session.pop("password_reset", None)

        # Finalmente lo devuelve al login.
        return redirect("/login")
    except Exception:
        # Si algo falla en el proceso, vuelve al inicio de recuperación.
        return redirect("/password/email")


def restablecer_password_link(request):
    token = (request.GET.get("token") or request.POST.get("token") or "").strip()
    if not token:
        return render(
            request,
            "auth/reset_password_link.html",
            {"error": "El enlace de recuperacion no es valido."},
            status=400,
        )

    usuario_id, error_token = _helper.validar_token_recuperacion(token)
    usuario = Usuario.objects.filter(pk=usuario_id).first() if usuario_id else None

    if request.method != "POST":
        if not usuario:
            return render(
                request,
                "auth/reset_password_link.html",
                {"token": token, "error": error_token or "El enlace de recuperacion no es valido."},
                status=400,
            )
        return render(
            request,
            "auth/reset_password_link.html",
            {
                "token": token,
                "email": usuario.correo or "",
                "password_policy_help": PASSWORD_POLICY_HELP,
            },
        )

    if not usuario:
        return render(
            request,
            "auth/reset_password_link.html",
            {"token": token, "error": error_token or "El enlace de recuperacion no es valido."},
            status=400,
        )

    password = request.POST.get("password", "")
    password_confirm = request.POST.get("password_confirm", "")

    if password != password_confirm:
        return render(
            request,
            "auth/reset_password_link.html",
            {
                "token": token,
                "email": usuario.correo or "",
                "error": "Las contrasenas no coinciden.",
                "password_policy_help": PASSWORD_POLICY_HELP,
            },
        )

    clave_valida, error_clave = validar_contrasena_segura(password)
    if not clave_valida:
        return render(
            request,
            "auth/reset_password_link.html",
            {
                "token": token,
                "email": usuario.correo or "",
                "error": error_clave,
                "password_policy_help": PASSWORD_POLICY_HELP,
            },
        )

    usuario.clave = hash_contrasena(password)
    usuario.save(update_fields=["clave"])
    _helper.limpiar_token_api(token)
    registrar_movimiento(
        request,
        f"Restablecimiento de contrasena por enlace para {usuario.nombre_completo() or usuario.correo or usuario.id_usuario}.",
    )
    return redirect("/login")


@csrf_exempt
def api_password_request_code(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    try:
        import json

        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalido"}, status=400)

    email = (data.get("correo") or "").strip().lower()
    if not email:
        return JsonResponse({"error": "El correo es obligatorio."}, status=400)

    usuario = _helper.buscar_usuario_por_correo(email)
    if not usuario:
        return JsonResponse({"error": "No existe un usuario asociado a ese correo."}, status=404)

    if not _helper.correo_configurado():
        return JsonResponse(
            {
                "error": "El servicio de correo no esta configurado en el servidor.",
            },
            status=503,
        )

    try:
        code = _helper.codigo_recuperacion()
        _helper.guardar_codigo_api(email, code)
        contexto = _helper.construir_contexto_correo(usuario, code)
        _helper.enviar_correo_recuperacion(email, contexto)
        return JsonResponse(
            {
                "ok": True,
                "correo": email,
                "ttl_minutes": settings.PASSWORD_RESET_CODE_TTL_MINUTES,
                "mensaje": "Se envio un codigo de seguridad al correo registrado.",
            }
        )
    except Exception as exc:
        return JsonResponse(
            {"error": _helper.mensaje_error_envio(exc)},
            status=500,
        )


@csrf_exempt
def api_password_reset(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    try:
        import json

        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalido"}, status=400)

    email = (data.get("correo") or "").strip().lower()
    code = (data.get("codigo") or "").strip()
    password = data.get("password") or ""
    password_confirm = data.get("password_confirm") or ""

    if not email or not code or not password or not password_confirm:
        return JsonResponse(
            {"error": "Correo, codigo y ambas contrasenas son obligatorios."},
            status=400,
        )

    reset_data = _helper.leer_codigo_api(email)
    codigo_valido, error = _helper.validar_sesion_recuperacion(reset_data, email, code)
    if not codigo_valido:
        return JsonResponse({"error": error}, status=400)

    if password != password_confirm:
        return JsonResponse({"error": "Las contrasenas no coinciden."}, status=400)

    clave_valida, error_clave = validar_contrasena_segura(password)
    if not clave_valida:
        return JsonResponse({"error": error_clave}, status=400)

    usuario = _helper.buscar_usuario_por_correo(email)
    if not usuario:
        return JsonResponse({"error": "No existe un usuario asociado a ese correo."}, status=404)

    usuario.clave = hash_contrasena(password)
    usuario.save(update_fields=["clave"])
    _helper.limpiar_codigo_api(email)

    return JsonResponse(
        {
            "ok": True,
            "mensaje": "La contrasena fue actualizada correctamente.",
        }
    )


@csrf_exempt
def api_forgot_password(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    try:
        import json

        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalido"}, status=400)

    correo = (data.get("correo") or "").strip().lower()
    respuesta = {
        "message": "Si el correo esta registrado, recibiras un enlace de recuperacion.",
    }
    if not correo:
        return JsonResponse(respuesta)

    usuario = _helper.buscar_usuario_por_correo(correo)
    if not usuario:
        return JsonResponse(respuesta)

    try:
        token = _helper.generar_token_recuperacion(usuario.id_usuario)
        reset_url = _helper.construir_url_recuperacion(request, token)
        _helper.guardar_token_api(correo, token)
        contexto = _helper.construir_contexto_enlace(usuario, reset_url)

        if settings.DEMO_MODE:
            registrar_movimiento(request, f"Solicitud de recuperacion en modo demo para {correo}.")
            return JsonResponse(
                {
                    **respuesta,
                    "demo_mode": True,
                    "reset_url": reset_url,
                    "token": token,
                }
            )

        _helper.enviar_correo_enlace_recuperacion(correo, contexto)
        registrar_movimiento(request, f"Solicitud de recuperacion enviada por correo para {correo}.")
    except Exception as exc:
        registrar_movimiento(request, f"Fallo enviando recuperacion por enlace para {correo}: {exc}.")

    return JsonResponse(respuesta)


@csrf_exempt
def api_reset_password(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    try:
        import json

        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalido"}, status=400)

    token = (data.get("token") or "").strip()
    password = (data.get("nueva_password") or data.get("password") or "").strip()

    if not token or not password:
        return JsonResponse({"error": "Token y nueva_password son obligatorios."}, status=400)

    usuario_id, error_token = _helper.validar_token_recuperacion(token)
    if not usuario_id:
        return JsonResponse({"error": error_token}, status=400)

    token_data = _helper.leer_token_api(token)
    if not token_data:
        return JsonResponse({"error": "El enlace de recuperacion ya fue usado o vencio."}, status=400)

    usuario = Usuario.objects.filter(pk=usuario_id).first()
    if not usuario:
        return JsonResponse({"error": "No existe un usuario asociado a ese enlace."}, status=404)

    clave_valida, error_clave = validar_contrasena_segura(password)
    if not clave_valida:
        return JsonResponse({"error": error_clave}, status=400)

    usuario.clave = hash_contrasena(password)
    usuario.save(update_fields=["clave"])
    _helper.limpiar_token_api(token)
    registrar_movimiento(request, f"Restablecimiento de contrasena por enlace para {usuario.nombre_completo() or usuario.correo or usuario.id_usuario}.")
    return JsonResponse({"ok": True, "message": "La contrasena fue actualizada correctamente."})
