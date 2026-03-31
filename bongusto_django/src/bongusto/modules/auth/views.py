"""Vistas de autenticacion con un flujo simple y facil de seguir."""

from datetime import datetime, timedelta
from email.mime.image import MIMEImage
from pathlib import Path
from secrets import randbelow

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.cache import never_cache

from bongusto.application.services import UsuarioService
from bongusto.domain.models import Usuario
from bongusto.modules.shared.audit import registrar_movimiento
from bongusto.modules.shared.security import (
    PASSWORD_POLICY_HELP,
    hash_contrasena,
    validar_contrasena_segura,
)


_service = UsuarioService()


class AuthPageHelper:
    """Agrupa pasos repetidos para dejar las vistas cortas."""

    def contexto_login(self, error=""):
        return {"error": error} if error else {}

    def contexto_email(self, email="", error=""):
        return {"email": email, "error": error}

    def contexto_reset(self, email="", error=""):
        return {
            "email": email,
            "error": error,
            "password_policy_help": PASSWORD_POLICY_HELP,
        }

    def crear_sesion_recuperacion(self, email, code):
        vence = timezone.now() + timedelta(minutes=settings.PASSWORD_RESET_CODE_TTL_MINUTES)
        return {
            "email": email,
            "code": code,
            "expires_at": vence.isoformat(),
        }

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
            if timezone.is_naive(expires_at):
                expires_at = timezone.make_aware(expires_at, timezone.get_current_timezone())
        except ValueError:
            return False, "La solicitud de recuperacion no es valida."

        if timezone.now() > expires_at:
            return False, "El codigo de verificacion ya vencio. Solicita uno nuevo."

        return True, ""

    def buscar_usuario_por_correo(self, email):
        return Usuario.objects.filter(correo__iexact=email).first()

    def autenticar(self, correo, clave):
        return _service.autenticar(correo, clave)

    def guardar_sesion_login(self, request, usuario):
        request.session.cycle_key()
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre
        request.session["usuario_tipo"] = usuario.tipo_usuario
        request.session.set_expiry(3600)

    def codigo_recuperacion(self):
        return f"{randbelow(1_000_000):06d}"

    def correo_configurado(self):
        return bool(settings.EMAIL_HOST_PASSWORD)

    def construir_contexto_correo(self, usuario, code):
        return {
            "nombre_usuario": usuario.nombre_completo() or usuario.correo or "usuario",
            "code": code,
            "ttl_minutes": settings.PASSWORD_RESET_CODE_TTL_MINUTES,
            "support_email": settings.DEFAULT_FROM_EMAIL,
        }

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


_helper = AuthPageHelper()


def redirect_root(request):
    return redirect("/login")


def login_view(request):
    if request.method != "POST":
        return render(request, "auth/login.html")

    try:
        correo = (request.POST.get("username", "") or "").strip().lower()
        clave = request.POST.get("password", "")
        usuario = _helper.autenticar(correo, clave)

        if not usuario:
            return render(request, "auth/login.html", _helper.contexto_login("Correo o contrasena incorrectos"))

        _helper.guardar_sesion_login(request, usuario)
        registrar_movimiento(
            request,
            f"Inicio de sesion del usuario {usuario.nombre_completo() or usuario.correo or usuario.id_usuario}.",
        )
        return redirect("/dashboard")
    except Exception:
        return render(
            request,
            "auth/login.html",
            _helper.contexto_login("No fue posible iniciar sesion en este momento."),
        )


@never_cache
def logout_view(request):
    try:
        usuario_nombre = request.session.get("usuario_nombre", "Usuario")
        registrar_movimiento(request, f"Cierre de sesion del usuario {usuario_nombre}.")
        request.session.flush()
        response = render(request, "auth/logout.html")
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        return response
    except Exception:
        request.session.flush()
        return redirect("/login")


def password_email(request):
    if request.method == "GET":
        return render(request, "auth/email.html")

    email = (request.POST.get("email", "") or "").strip().lower()

    try:
        usuario = _helper.buscar_usuario_por_correo(email)
        if not usuario:
            return render(
                request,
                "auth/email.html",
                _helper.contexto_email(email, "No existe un usuario asociado a ese correo."),
            )

        if not _helper.correo_configurado():
            return render(
                request,
                "auth/email.html",
                _helper.contexto_email(
                    email,
                    "En este momento el servicio de recuperacion por correo no esta disponible. Intenta de nuevo mas tarde o revisa la configuracion del servidor.",
                ),
            )

        code = _helper.codigo_recuperacion()
        request.session["password_reset"] = _helper.crear_sesion_recuperacion(email, code)
        request.session.modified = True

        contexto = _helper.construir_contexto_correo(usuario, code)
        _helper.enviar_correo_recuperacion(email, contexto)
        return redirect(f"/password/reset?email={email}")
    except Exception:
        return render(
            request,
            "auth/email.html",
            _helper.contexto_email(
                email,
                "No fue posible enviar el codigo de recuperacion en este momento.",
            ),
        )


def password_reset(request):
    email = request.GET.get("email", "")

    if request.method != "POST":
        return render(request, "auth/reset_password.html", _helper.contexto_reset(email))

    try:
        email = (request.POST.get("email", "") or "").strip().lower()
        code = (request.POST.get("code", "") or "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        reset_data = request.session.get("password_reset")
        codigo_valido, error = _helper.validar_sesion_recuperacion(reset_data, email, code)
        if not codigo_valido:
            return render(request, "auth/reset_password.html", _helper.contexto_reset(email, error))

        if password != password_confirm:
            return render(
                request,
                "auth/reset_password.html",
                _helper.contexto_reset(email, "Las contrasenas no coinciden."),
            )

        clave_valida, error_clave = validar_contrasena_segura(password)
        if not clave_valida:
            return render(request, "auth/reset_password.html", _helper.contexto_reset(email, error_clave))

        usuario = _helper.buscar_usuario_por_correo(email)
        if not usuario:
            return render(
                request,
                "auth/reset_password.html",
                _helper.contexto_reset(email, "No existe un usuario asociado a ese correo."),
            )

        usuario.clave = hash_contrasena(password)
        usuario.save(update_fields=["clave"])
        request.session.pop("password_reset", None)
        return redirect("/login")
    except Exception:
        return redirect("/password/email")
