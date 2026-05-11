"""Modulo compartido de seguridad.

Aqui se centralizan todas las validaciones y funciones relacionadas
con contrasenas para poder reutilizarlas en diferentes partes del sistema.
"""

import re

from django.contrib.auth.hashers import check_password, identify_hasher, make_password


# Expresion general que define TODA la politica de contrasenas del sistema.
# Esta regex valida todo en una sola linea.
PASSWORD_POLICY_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&.\-_#])[A-Za-z\d@$!%*?&.\-_#]{8,}$")

# Mensaje general que se muestra cuando no cumple la politica completa.
PASSWORD_POLICY_HELP = "La contrasena debe tener minimo 8 caracteres, al menos una mayuscula, una minuscula, un numero y un caracter especial."

# Estas regex son mas pequenas y sirven para validar cada regla por separado.
# Esto permite dar mensajes mas claros al usuario.
MAYUSCULA_REGEX = re.compile(r"[A-Z]")
MINUSCULA_REGEX = re.compile(r"[a-z]")
NUMERO_REGEX = re.compile(r"\d")
ESPECIAL_REGEX = re.compile(r"[@$!%*?&.\-_#]")


def validar_contrasena_segura(clave):
    """Valida la contrasena paso a paso para dar mensajes mas claros al usuario."""
    # Se limpia la clave para evitar errores por espacios.
    clave = (clave or "").strip()

    # Validaciones una a una (esto ayuda a dar feedback especifico).
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

    # Validacion final completa (refuerzo de seguridad).
    if not PASSWORD_POLICY_REGEX.match(clave):
        return False, PASSWORD_POLICY_HELP

    return True, ""


def es_hash_django(valor):
    """Detecta si el valor ya esta guardado como hash usando el sistema de Django."""
    try:
        # Django intenta identificar el tipo de hash.
        identify_hasher(valor or "")
        return True
    except ValueError:
        # Si falla, significa que no es un hash valido.
        return False


def hash_contrasena(clave):
    """Convierte una contrasena en texto plano a un hash seguro."""
    # Siempre se limpia antes de generar el hash.
    return make_password((clave or "").strip())


def verificar_contrasena_usuario(usuario, clave_plana):
    """Verifica la contrasena del usuario y migra automaticamente las antiguas."""
    # Se obtiene la clave guardada en la base de datos.
    clave_guardada = (getattr(usuario, "clave", None) or "").strip()
    clave_plana = clave_plana or ""

    # Si falta alguna de las dos, no se puede validar.
    if not clave_guardada or not clave_plana:
        return False

    # Flujo normal: cuando la contrasena ya esta protegida con hash.
    if es_hash_django(clave_guardada):
        return check_password(clave_plana, clave_guardada)

    # Compatibilidad con registros antiguos (cuando se guardaban en texto plano).
    # Si coincide, se aprovecha para migrarla a hash automaticamente.
    if clave_guardada == clave_plana:
        usuario.clave = hash_contrasena(clave_plana)
        usuario.save(update_fields=["clave"])
        return True

    return False


# Se define lo que este modulo expone al resto del sistema.
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