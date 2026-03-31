"""Modulo compartido de seguridad.

Aqui se agrupan las validaciones y helpers relacionados con contrasenas
para reutilizarlos en varios modulos del sistema.
"""

import re

from django.contrib.auth.hashers import check_password, identify_hasher, make_password


# Expresion general de la politica de contrasenas del sistema.
PASSWORD_POLICY_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&.\-_#])[A-Za-z\d@$!%*?&.\-_#]{8,}$")
PASSWORD_POLICY_HELP = "La contrasena debe tener minimo 8 caracteres, al menos una mayuscula, una minuscula, un numero y un caracter especial."

# Expresiones pequenas para validar cada regla de forma separada.
MAYUSCULA_REGEX = re.compile(r"[A-Z]")
MINUSCULA_REGEX = re.compile(r"[a-z]")
NUMERO_REGEX = re.compile(r"\d")
ESPECIAL_REGEX = re.compile(r"[@$!%*?&.\-_#]")


def validar_contrasena_segura(clave):
    """Valida la contrasena paso a paso y retorna mensaje claro."""
    clave = (clave or "").strip()

    if not clave:
        return False, "La contrasena es obligatoria."
    if len(clave) < 8:
        return False, "La contrasena debe tener minimo 8 caracteres."
    if not MAYUSCULA_REGEX.search(clave):
        return False, "La contrasena debe incluir al menos una letra mayuscula."
    if not MINUSCULA_REGEX.search(clave):
        return False, "La contrasena debe incluir al menos una letra minuscula."
    if not NUMERO_REGEX.search(clave):
        return False, "La contrasena debe incluir al menos un numero."
    if not ESPECIAL_REGEX.search(clave):
        return False, "La contrasena debe incluir al menos un caracter especial."
    if not PASSWORD_POLICY_REGEX.match(clave):
        return False, PASSWORD_POLICY_HELP

    return True, ""


def es_hash_django(valor):
    """Indica si un valor ya esta almacenado como hash de Django."""
    try:
        identify_hasher(valor or "")
        return True
    except ValueError:
        return False


def hash_contrasena(clave):
    """Genera el hash de una contrasena en texto plano."""
    return make_password((clave or "").strip())


def verificar_contrasena_usuario(usuario, clave_plana):
    """Verifica la contrasena y migra valores antiguos sin hash."""
    clave_guardada = (getattr(usuario, "clave", None) or "").strip()
    clave_plana = clave_plana or ""

    if not clave_guardada or not clave_plana:
        return False

    # Flujo normal cuando la contrasena ya esta guardada de forma segura.
    if es_hash_django(clave_guardada):
        return check_password(clave_plana, clave_guardada)

    # Compatibilidad con registros antiguos guardados en texto plano.
    if clave_guardada == clave_plana:
        usuario.clave = hash_contrasena(clave_plana)
        usuario.save(update_fields=["clave"])
        return True

    return False


__all__ = [
    "ESPECIAL_REGEX",
    "MAYUSCULA_REGEX",
    "MINUSCULA_REGEX",
    "NUMERO_REGEX",
    "PASSWORD_POLICY_HELP",
    "PASSWORD_POLICY_REGEX",
    "es_hash_django",
    "hash_contrasena",
    "validar_contrasena_segura",
    "verificar_contrasena_usuario",
]
