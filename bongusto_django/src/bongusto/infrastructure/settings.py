"""
infrastructure/settings.py
Aquí está toda la configuración principal de Django para BonGusto.
"""

import os
from pathlib import Path
from urllib.parse import urlparse

# Ruta base del proyecto.
# Desde aquí se construyen todas las demás rutas (archivos, static, media, etc.)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def _load_dotenv(path: Path) -> None:
    """Carga variables desde un archivo .env simple sin depender de paquetes extra."""
    if not path.exists():
        return

    with path.open("r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv(BASE_DIR / ".env")

# Clave secreta por defecto (solo para desarrollo).
_DEFAULT_SECRET_KEY = "django-dev-bongusto-cambia-esta-clave"

# Intenta tomar la clave desde variables de entorno.
# Si no encuentra nada, usa la de desarrollo.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", _DEFAULT_SECRET_KEY)

# Define el entorno del proyecto (development o production).
DJANGO_ENV = os.getenv("DJANGO_ENV", "development").strip().lower()

# DEBUG:
# True en desarrollo → muestra errores detallados
# False en producción → oculta errores sensibles
DEBUG = os.getenv("DJANGO_DEBUG", "true" if DJANGO_ENV != "production" else "false").lower() == "true"

# Hosts permitidos (desde variables de entorno).
_allowed_hosts_from_env = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")

# Convierte los hosts en lista y limpia espacios.
ALLOWED_HOSTS = [
    host.strip()
    for host in _allowed_hosts_from_env.split(",")
    if host.strip()
]

# En desarrollo, si no hay hosts definidos, permite todo (*)
if DEBUG and _allowed_hosts_from_env.strip() in {"", "127.0.0.1,localhost"}:
    ALLOWED_HOSTS = ["*"]

# Agrega hosts básicos para pruebas si no están.
for host_pruebas in ("testserver", "localhost", "127.0.0.1"):
    if host_pruebas not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host_pruebas)

# Seguridad importante:
# En producción NO se puede usar la clave por defecto.
if DJANGO_ENV == "production" and not DEBUG and SECRET_KEY == _DEFAULT_SECRET_KEY:
    raise RuntimeError(
        "Debes definir DJANGO_SECRET_KEY en el entorno cuando DJANGO_DEBUG=false."
    )

# Apps instaladas en el proyecto.
INSTALLED_APPS = [
    "daphne",  # Servidor ASGI (para WebSockets)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",  # Soporte para WebSocket (chat en tiempo real)

    # Apps propias de BonGusto
    "bongusto.domain",
    "bongusto.interfaces",
    "bongusto.modules.auth.apps.AuthConfig",
    "bongusto.modules.bitacora.apps.BitacoraConfig",
    "bongusto.modules.calificaciones.apps.CalificacionesConfig",
    "bongusto.modules.categorias.apps.CategoriasConfig",
    "bongusto.modules.chat.apps.ChatConfig",
    "bongusto.modules.dashboard.apps.DashboardConfig",
    "bongusto.modules.eventos.apps.EventosConfig",
    "bongusto.modules.menus.apps.MenusConfig",
    "bongusto.modules.mesas.apps.MesasConfig",
    "bongusto.modules.musica.apps.MusicaConfig",
    "bongusto.modules.notificaciones.apps.NotificacionesConfig",
    "bongusto.modules.pedidos.apps.PedidosConfig",
    "bongusto.modules.perfil.apps.PerfilConfig",
    "bongusto.modules.permisos.apps.PermisosConfig",
    "bongusto.modules.productos.apps.ProductosConfig",
    "bongusto.modules.roles.apps.RolesConfig",
    "bongusto.modules.shared.apps.SharedConfig",
    "bongusto.modules.usuarios.apps.UsuariosConfig",
]

# Middleware → se ejecuta en cada petición
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Middleware propio de BonGusto (manejo de sesiones / auth)
    "bongusto.modules.shared.middleware.AuthMiddleware",
]

# Archivo principal de rutas
ROOT_URLCONF = "bongusto.interfaces.urls"

# Configuración de templates (HTML)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Aquí podrías agregar rutas manuales si quisieras
        "APP_DIRS": True,  # Usa los templates dentro de cada app
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ASGI → necesario para WebSockets (chat)
ASGI_APPLICATION = "bongusto.infrastructure.asgi.application"

# Base de datos (MySQL)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "bongustofi"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}

# Configuración de WebSockets (Channels)
REDIS_URL = os.getenv("REDIS_URL", "").strip()

if REDIS_URL:
    parsed_redis = urlparse(REDIS_URL)

    # Construye la URL de conexión a Redis
    _redis_location = (
        f"redis://{parsed_redis.hostname or '127.0.0.1'}:{parsed_redis.port or 6379}"
        f"/{(parsed_redis.path or '/0').lstrip('/') or '0'}"
    )

    # Channels usando Redis (recomendado en producción)
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
                "capacity": int(os.getenv("CHANNEL_CAPACITY", "300")),
                "expiry": int(os.getenv("CHANNEL_EXPIRY_SECONDS", "30")),
            },
        }
    }

    # Cache también en Redis
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": _redis_location,
            "TIMEOUT": int(os.getenv("CACHE_DEFAULT_TIMEOUT_SECONDS", "300")),
            "KEY_PREFIX": os.getenv("CACHE_KEY_PREFIX", "bongusto"),
        }
    }
else:
    # Sin Redis → todo en memoria (solo desarrollo)
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "bongusto-local-cache",
            "TIMEOUT": int(os.getenv("CACHE_DEFAULT_TIMEOUT_SECONDS", "120")),
        }
    }

# Idioma y zona horaria
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# Archivos estáticos (CSS, JS, imágenes)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Archivos subidos (media)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Tipo de ID automático
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuración de sesión
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 3600  # dura 1 hora
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG  # solo seguro en producción

# Configuración CSRF
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG

# Seguridad del navegador
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

# HSTS (solo producción)
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# Redirección automática a HTTPS
SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "false" if DEBUG else "true").lower() == "true"

# Configuración de correo (SMTP)
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"

# Correo que envía el sistema
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "no-reply@bongusto.local")

# Tiempo de validez del código de recuperación
PASSWORD_RESET_CODE_TTL_MINUTES = int(os.getenv("PASSWORD_RESET_CODE_TTL_MINUTES", "10"))

# Modo de demostración para el flujo de recuperación por enlace.
# Solo se activa explícitamente desde el entorno; por defecto usa SMTP real.
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Tiempo de vida del token de enlace de recuperación.
PASSWORD_RESET_TOKEN_TTL_SECONDS = int(os.getenv("PASSWORD_RESET_TOKEN_TTL_SECONDS", "3600"))

# Tiempo de vida del token de API
_default_api_token_ttl = 60 * 60 * 24 * 30 if DEBUG else 60 * 60 * 8
API_TOKEN_TTL_SECONDS = int(os.getenv("API_TOKEN_TTL_SECONDS", str(_default_api_token_ttl)))
