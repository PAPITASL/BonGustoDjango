"""Vistas del perfil con un flujo corto y directo."""

import json

from django.http import JsonResponse
from django.shortcuts import redirect, render

# Servicio de usuario
from bongusto.application.services import UsuarioService

# Registro de acciones (bitacora)
from bongusto.modules.shared.audit import registrar_movimiento
from bongusto.modules.shared.api_auth import api_login_required, emitir_api_token
from bongusto.modules.shared.table_state import MesaStateService

# Funciones de seguridad para contraseñas
from bongusto.modules.shared.security import (
    PASSWORD_POLICY_HELP,
    hash_contrasena,
    validar_contrasena_segura,
    verificar_contrasena_usuario,
)

# Instancia del servicio
_service = UsuarioService()
_mesa_service = MesaStateService()

class PerfilPageHelper:
    """Agrupa la logica del perfil para no repetir codigo."""

    # Obtiene el usuario actual desde la sesion
    def usuario_actual(self, request):
        usuario_id = request.session.get("usuario_id")
        return _service.buscar_por_id(usuario_id)

    # Contexto que se envia a la vista de edicion
    def contexto_edicion(self, usuario, error=""):
        return {
            "usuario": usuario,
            "password_policy_help": PASSWORD_POLICY_HELP,
            "error": error,
        }

    # Carga los datos del formulario al usuario
    def cargar_desde_post(self, request, usuario):
        usuario.nombre = request.POST.get("nombre", usuario.nombre)
        usuario.correo = (request.POST.get("correo", usuario.correo) or "").strip().lower()
        usuario.telefono = request.POST.get("telefono", usuario.telefono)
        return usuario

    def split_nombre_completo(self, valor):
        nombre_completo = (valor or "").strip()
        if not nombre_completo:
            return "", ""
        partes = nombre_completo.split()
        nombre = partes[0]
        apellido = " ".join(partes[1:]) if len(partes) > 1 else ""
        return nombre, apellido

    def usuario_a_payload(self, usuario):
        mesa = _mesa_service.mesa_por_usuario(usuario.id_usuario)
        return {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre or "",
            "apellido": usuario.apellido or "",
            "nombre_completo": usuario.nombre_completo(),
            "correo": usuario.correo or "",
            "telefono": usuario.telefono or "",
            "tipo_usuario": usuario.tipo_usuario or "",
            "estado": usuario.estado or "",
            "mesa_id": mesa.get("id") if mesa else None,
            "mesa_numero": mesa.get("numero_mesa") if mesa else None,
            "mesa_label": mesa.get("etiqueta") if mesa else "",
            "mesa_estado": mesa.get("estado") if mesa else "",
            "api_token": emitir_api_token(usuario),
        }

# Instancia del helper
_helper = PerfilPageHelper()


def _leer_json_request(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "JSON invalido"}, status=400)

# Vista para ver el perfil
def ver(request):
    try:
        usuario = _helper.usuario_actual(request)
        if not usuario:
            return redirect("/login")
        return render(request, "perfil/index.html", {"usuario": usuario})
    except Exception:
        return redirect("/login")

# Vista para editar el perfil
def editar(request):
    try:
        usuario = _helper.usuario_actual(request)
        if not usuario:
            return redirect("/login")
        return render(request, "perfil/edit.html", _helper.contexto_edicion(usuario))
    except Exception:
        return redirect("/perfil")

# Vista para actualizar los datos
def actualizar(request):
    if request.method != "POST":
        return redirect("/perfil")

    try:
        usuario = _helper.usuario_actual(request)
        if not usuario:
            return redirect("/login")

        # Carga los datos del formulario
        usuario = _helper.cargar_desde_post(request, usuario)
        nueva_clave = (request.POST.get("nueva_clave") or "").strip()

        # Si el usuario quiere cambiar contraseña
        if nueva_clave:
            clave_valida, error_clave = validar_contrasena_segura(nueva_clave)
            if not clave_valida:
                return render(request, "perfil/edit.html", _helper.contexto_edicion(usuario, error_clave))
            usuario.clave = hash_contrasena(nueva_clave)

        # Guarda cambios
        _service.guardar(usuario)

        # Actualiza nombre en sesion
        request.session["usuario_nombre"] = usuario.nombre

        # Registra movimiento en bitacora
        registrar_movimiento(
            request,
            f"Actualizacion de perfil del usuario {usuario.nombre_completo() or usuario.correo or usuario.id_usuario}.",
        )

        return redirect("/perfil")

    except Exception:
        return redirect("/perfil")


@api_login_required()
def api_actualizar_perfil(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    data, error = _leer_json_request(request)
    if error:
        return error

    usuario = request.api_user
    nombre_completo = (data.get("nombre_completo") or data.get("nombre") or "").strip()
    correo = (data.get("correo") or usuario.correo or "").strip().lower()
    telefono = (data.get("telefono") or usuario.telefono or "").strip()

    if not nombre_completo or not correo:
        return JsonResponse({"error": "Nombre y correo son obligatorios."}, status=400)

    existente = _service.buscar_por_correo(correo)
    if existente and existente.id_usuario != usuario.id_usuario:
        return JsonResponse({"error": "El correo ya esta registrado."}, status=400)

    nombre, apellido = _helper.split_nombre_completo(nombre_completo)
    usuario.nombre = nombre
    usuario.apellido = apellido
    usuario.correo = correo
    usuario.telefono = telefono

    try:
        _service.guardar(usuario)
    except Exception as exc:
        return JsonResponse({"error": f"No se pudo actualizar el perfil: {exc}"}, status=400)

    registrar_movimiento(
        request,
        f"Actualizacion de perfil API del usuario {usuario.nombre_completo() or usuario.correo or usuario.id_usuario}.",
    )
    return JsonResponse(
        {
            "message": "Perfil actualizado correctamente.",
            "usuario": _helper.usuario_a_payload(usuario),
        }
    )


@api_login_required()
def api_cambiar_contrasena(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    data, error = _leer_json_request(request)
    if error:
        return error

    usuario = request.api_user
    contrasena_actual = (data.get("contrasena_actual") or data.get("password_actual") or "").strip()
    nueva_contrasena = (data.get("nueva_contrasena") or data.get("password") or "").strip()
    confirmar_contrasena = (
        data.get("confirmar_contrasena")
        or data.get("password_confirm")
        or data.get("confirm_password")
        or ""
    ).strip()

    if not contrasena_actual or not nueva_contrasena or not confirmar_contrasena:
        return JsonResponse({"error": "Todos los campos son obligatorios."}, status=400)

    if nueva_contrasena != confirmar_contrasena:
        return JsonResponse({"error": "Las contrasenas no coinciden."}, status=400)

    if not usuario.clave or not verificar_contrasena_usuario(usuario, contrasena_actual):
        return JsonResponse({"error": "La contrasena actual no es correcta."}, status=400)

    clave_valida, error_clave = validar_contrasena_segura(nueva_contrasena)
    if not clave_valida:
        return JsonResponse({"error": error_clave}, status=400)

    usuario.clave = hash_contrasena(nueva_contrasena)

    try:
        _service.guardar(usuario)
    except Exception as exc:
        return JsonResponse({"error": f"No se pudo cambiar la contrasena: {exc}"}, status=400)

    registrar_movimiento(
        request,
        f"Cambio de contrasena API del usuario {usuario.nombre_completo() or usuario.correo or usuario.id_usuario}.",
    )
    return JsonResponse({"message": "Contrasena actualizada correctamente."})
