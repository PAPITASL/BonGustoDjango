"""
Vistas simples del modulo usuarios.

Se dejo en un estilo mas directo y facil de seguir para estudiantes que apenas
estan empezando con Python, POO y Django.
"""

import json
from collections import defaultdict

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from bongusto.application.services import RolService, UsuarioService
from bongusto.domain.models import Bitacora, PedidoEncabezado, Reserva, Rol, Usuario
from bongusto.infrastructure.pdf_generator import crear_pdf_compuesto
from bongusto.modules.shared.api_auth import emitir_api_token
from bongusto.modules.shared.audit import registrar_movimiento
from bongusto.modules.shared.table_state import MesaStateService
from bongusto.modules.shared.security import (
    PASSWORD_POLICY_HELP,
    hash_contrasena,
    validar_contrasena_segura,
)


class UsuarioPageHelper:
    """Ayuda a preparar datos de pantalla y del reporte."""

    TIPO_CHOICES = [
        ("cliente", "Cliente"),
        ("administrador", "Administrador"),
        ("mesero", "Mesero"),
        ("trabajador", "Trabajador"),
    ]

    def __init__(self):
        self.usuario_service = UsuarioService()
        self.rol_service = RolService()

    def roles_mesero(self):
        """Devuelve solo roles relacionados con mesero."""
        return list(Rol.objects.filter(nombre_rol__icontains="mesero").order_by("nombre_rol"))

    def rol_mesero_por_defecto(self):
        """Busca el primer rol de mesero disponible."""
        return Rol.objects.filter(nombre_rol__icontains="mesero").order_by("nombre_rol").first()

    def tipo_usuario_desde_rol(self, rol):
        """Convierte el rol en un tipo de usuario simple."""
        nombre_rol = ""
        if rol:
            nombre_rol = (rol.nombre_rol or "").strip().lower()

        if "admin" in nombre_rol:
            return "administrador"
        if "cliente" in nombre_rol:
            return "cliente"
        if "mesero" in nombre_rol:
            return "mesero"
        if nombre_rol:
            return "trabajador"
        return "mesero"

    def label_rol_o_tipo(self, usuario):
        """Devuelve el texto visible del rol o tipo."""
        if usuario and usuario.id_rol:
            return usuario.id_rol.nombre_rol

        tipo = ""
        if usuario:
            tipo = (usuario.tipo_usuario or "").strip().lower()

        if tipo == "administrador":
            return "Administrador"
        if tipo == "cliente":
            return "Cliente"
        if tipo == "trabajador":
            return "Trabajador"
        if tipo == "mesero":
            return "Mesero"
        return "Sin rol definido"

    def segmento_usuario(self, usuario):
        """Clasifica usuarios para el reporte."""
        tipo = (usuario.tipo_usuario or "").strip().lower()

        if tipo == "administrador":
            return "Admin"
        if tipo in {"trabajador", "mesero"}:
            return "Empleado"
        if tipo == "cliente":
            return "Cliente"

        rol_nombre = (usuario.get_rol_nombre() or "").strip().lower()
        if "admin" in rol_nombre:
            return "Admin"
        if rol_nombre:
            return "Empleado"
        return "Cliente"

    def contexto_form_crear(self, usuario=None, error=None):
        """Contexto del formulario para crear mesero."""
        if usuario is None:
            usuario = Usuario()

        try:
            roles = self.roles_mesero()
        except Exception:
            roles = []

        rol_default = roles[0] if roles else None

        return {
            "usuario": usuario,
            "roles": roles,
            "tipo_choices": [("mesero", "Mesero")],
            "readonly": False,
            "rol_mesero_default": rol_default,
            "tipo_preview": self.tipo_usuario_desde_rol(rol_default) if rol_default else "mesero",
            "password_policy_help": PASSWORD_POLICY_HELP,
            "error": error,
        }

    def contexto_form_ver(self, usuario):
        """Contexto del formulario de lectura."""
        try:
            roles = self.roles_mesero()
        except Exception:
            roles = []

        return {
            "usuario": usuario,
            "roles": roles,
            "tipo_choices": self.TIPO_CHOICES,
            "readonly": True,
            "accion": "Ver",
            "rol_o_tipo": self.label_rol_o_tipo(usuario),
            "password_policy_help": PASSWORD_POLICY_HELP,
        }

    def construir_reporte(self, usuarios):
        """Arma los bloques del PDF de usuarios."""
        usuarios = list(usuarios)
        resumen = self._resumen_actividad_por_usuario(usuarios)

        filas_principales = []
        roles = {"Admin": 0, "Empleado": 0, "Cliente": 0}
        clientes_nuevos = 0
        clientes_frecuentes = 0
        ranking_clientes = []
        crecimiento_por_mes = defaultdict(int)
        activos = 0
        inactivos = 0

        for usuario in usuarios:
            segmento = self.segmento_usuario(usuario)
            roles[segmento] = roles.get(segmento, 0) + 1

            if (usuario.estado or "").lower() == "activo":
                activos += 1
            if (usuario.estado or "").lower() == "inactivo":
                inactivos += 1

            actividad = resumen["por_usuario"].get(usuario.id_usuario, {})
            total_pedidos = actividad.get("pedidos", 0)
            total_reservas = actividad.get("reservas", 0)
            total_logs = actividad.get("logs", 0)
            primera_fecha = actividad.get("primera_fecha")

            if primera_fecha:
                clave_mes = (primera_fecha.year, primera_fecha.month)
                crecimiento_por_mes[clave_mes] += 1

            if segmento == "Cliente":
                if total_pedidos >= 2:
                    clientes_frecuentes += 1
                else:
                    clientes_nuevos += 1

                ranking_clientes.append(
                    [
                        usuario.nombre_completo() or f"Usuario {usuario.id_usuario}",
                        usuario.correo or "-",
                        str(total_pedidos),
                        usuario.estado or "-",
                    ]
                )

            filas_principales.append(
                [
                    str(usuario.id_usuario),
                    usuario.nombre_completo() or "-",
                    usuario.correo or "-",
                    segmento,
                    usuario.estado or "-",
                    f"Pedidos: {total_pedidos} | Reservas: {total_reservas} | Bitacora: {total_logs}",
                ]
            )

        ranking_clientes.sort(key=lambda fila: int(fila[2]), reverse=True)
        if not ranking_clientes:
            ranking_clientes.append(["Sin clientes", "-", "0", "-"])

        crecimiento_rows = []
        for (year, month), total in sorted(crecimiento_por_mes.items()):
            crecimiento_rows.append([f"{month:02d}/{year}", str(total)])
        if not crecimiento_rows:
            crecimiento_rows.append(["Sin actividad registrada", "0"])

        return [
            {
                "heading": "Tabla usuarios, roles, estados y actividad",
                "headers": ["ID", "Usuario", "Correo", "Rol", "Estado", "Actividad"],
                "rows": filas_principales,
                "col_widths": [
                    1.6 * 72 / 2.54,
                    4.0 * 72 / 2.54,
                    4.8 * 72 / 2.54,
                    2.2 * 72 / 2.54,
                    2.4 * 72 / 2.54,
                    9.0 * 72 / 2.54,
                ],
            },
            {
                "heading": "Usuarios activos vs inactivos",
                "headers": ["Estado", "Total"],
                "rows": [["Activos", str(activos)], ["Inactivos", str(inactivos)]],
            },
            {
                "heading": "Crecimiento de usuarios (por mes)",
                "paragraph": "Basado en la primera actividad registrada de cada usuario en pedidos, reservas o bitacora.",
                "headers": ["Mes", "Usuarios"],
                "rows": crecimiento_rows,
            },
            {
                "heading": "Usuarios por rol (admin / empleado / cliente)",
                "headers": ["Rol", "Total"],
                "rows": [[rol, str(total)] for rol, total in roles.items()],
            },
            {
                "heading": "Clientes frecuentes vs nuevos",
                "paragraph": "Se consideran frecuentes los clientes con 2 o mas pedidos registrados.",
                "headers": ["Segmento", "Total"],
                "rows": [
                    ["Clientes frecuentes", str(clientes_frecuentes)],
                    ["Clientes nuevos", str(clientes_nuevos)],
                ],
            },
            {
                "heading": "Ranking de clientes mas activos (mas pedidos)",
                "headers": ["Cliente", "Correo", "Pedidos", "Estado"],
                "rows": ranking_clientes[:10],
            },
        ]

    def _resumen_actividad_por_usuario(self, usuarios):
        """Cuenta pedidos, reservas, bitacora y primera actividad por usuario."""
        usuario_ids = [usuario.id_usuario for usuario in usuarios]
        datos = defaultdict(
            lambda: {
                "pedidos": 0,
                "reservas": 0,
                "logs": 0,
                "primera_fecha": None,
            }
        )

        self._sumar_pedidos(usuario_ids, datos)
        self._sumar_reservas(usuario_ids, datos)
        self._sumar_logs(usuario_ids, datos)

        return {"por_usuario": datos}

    def _sumar_pedidos(self, usuario_ids, datos):
        pedidos = PedidoEncabezado.objects.filter(id_usuario_id__in=usuario_ids).only(
            "id_usuario_id",
            "fecha_pedido",
        )
        for pedido in pedidos:
            if not pedido.id_usuario_id:
                continue
            datos[pedido.id_usuario_id]["pedidos"] += 1
            if pedido.fecha_pedido:
                self._guardar_primera_fecha(datos[pedido.id_usuario_id], pedido.fecha_pedido)

    def _sumar_reservas(self, usuario_ids, datos):
        reservas = Reserva.objects.filter(id_usuario_id__in=usuario_ids).only(
            "id_usuario_id",
            "fecha_reser",
        )
        for reserva in reservas:
            if not reserva.id_usuario_id:
                continue
            datos[reserva.id_usuario_id]["reservas"] += 1
            if reserva.fecha_reser:
                self._guardar_primera_fecha(datos[reserva.id_usuario_id], reserva.fecha_reser)

    def _sumar_logs(self, usuario_ids, datos):
        logs = Bitacora.objects.filter(id_usuario_id__in=usuario_ids).only(
            "id_usuario_id",
            "fecha_accion",
        )
        for log in logs:
            if not log.id_usuario_id:
                continue
            datos[log.id_usuario_id]["logs"] += 1
            if log.fecha_accion:
                self._guardar_primera_fecha(datos[log.id_usuario_id], log.fecha_accion.date())

    def _guardar_primera_fecha(self, resumen_usuario, fecha):
        actual = resumen_usuario["primera_fecha"]
        if actual is None or fecha < actual:
            resumen_usuario["primera_fecha"] = fecha


helper = UsuarioPageHelper()
usuario_service = helper.usuario_service
mesa_service = MesaStateService()


def index(request):
    """Muestra el listado principal de usuarios."""
    nombre = request.GET.get("nombre", "")
    correo = request.GET.get("correo", "")
    rol = request.GET.get("rol", "")
    estado = request.GET.get("estado", "")

    try:
        usuarios = usuario_service.listar_filtrado(nombre, correo, rol, estado)
    except Exception:
        usuarios = []

    contexto = {
        "usuarios": usuarios,
        "filtros": {
            "nombre": nombre,
            "correo": correo,
            "rol": rol,
            "estado": estado,
        },
    }
    return render(request, "usuario/index.html", contexto)


def create(request):
    """Muestra el formulario para crear mesero."""
    return render(request, "usuario/create.html", helper.contexto_form_crear())


def ver(request, pk):
    """Muestra el detalle del usuario."""
    try:
        usuario = usuario_service.buscar_por_id(pk)
    except Exception:
        usuario = None

    if not usuario:
        return redirect("/usuarios")

    return render(request, "usuario/edit.html", helper.contexto_form_ver(usuario))


def store(request):
    """Guarda un nuevo usuario tipo mesero."""
    if request.method != "POST":
        return redirect("/usuarios")

    clave = request.POST.get("clave", "")
    clave_valida, error_clave = validar_contrasena_segura(clave)

    usuario_preview = Usuario(
        nombre=request.POST.get("nombre", ""),
        apellido=request.POST.get("apellido", ""),
        correo=request.POST.get("correo", ""),
        telefono=request.POST.get("telefono", ""),
        estado="Activo",
        tipo_usuario="mesero",
    )

    if not clave_valida:
        contexto = helper.contexto_form_crear(usuario_preview, error_clave)
        return render(request, "usuario/create.html", contexto)

    try:
        usuario = Usuario()
        usuario.nombre = request.POST.get("nombre", "")
        usuario.apellido = request.POST.get("apellido", "")
        usuario.correo = (request.POST.get("correo", "") or "").strip().lower()
        usuario.clave = hash_contrasena(clave)
        usuario.telefono = request.POST.get("telefono", "")
        usuario.estado = "Activo"
        usuario.tipo_usuario = "mesero"

        rol_id = request.POST.get("id_rol")
        rol_mesero = None
        if rol_id:
            rol_mesero = Rol.objects.filter(
                pk=rol_id,
                nombre_rol__icontains="mesero",
            ).first()

        usuario.id_rol = rol_mesero or helper.rol_mesero_por_defecto()
        usuario.tipo_usuario = helper.tipo_usuario_desde_rol(usuario.id_rol)

        usuario_service.guardar(usuario)

        registrar_movimiento(
            request,
            f"Creacion de usuario tipo mesero {usuario.nombre_completo() or usuario.correo or usuario.id_usuario}.",
        )
        return redirect("/usuarios")
    except Exception:
        contexto = helper.contexto_form_crear(
            usuario_preview,
            "No fue posible guardar el usuario.",
        )
        return render(request, "usuario/create.html", contexto)


def edit(request, pk):
    """No edita desde esta pantalla. Redirige al detalle."""
    return redirect(f"/usuarios/{pk}")


def update(request, pk):
    """No actualiza desde esta pantalla. Redirige al detalle."""
    return redirect(f"/usuarios/{pk}")


def toggle_estado(request, pk):
    """Activa o desactiva un usuario."""
    if request.method != "POST":
        return redirect("/usuarios")

    try:
        usuario = usuario_service.buscar_por_id(pk)
        if usuario:
            if usuario.estado == "Activo":
                usuario.estado = "Inactivo"
            else:
                usuario.estado = "Activo"

            usuario_service.guardar(usuario)
            registrar_movimiento(
                request,
                f"Cambio de estado del usuario {usuario.nombre_completo() or usuario.correo or usuario.id_usuario} a {usuario.estado}.",
            )
    except Exception:
        pass

    return redirect("/usuarios")


def delete(request, pk):
    """No elimina usuarios desde esta vista."""
    return redirect("/usuarios")


def reporte(request):
    """Genera el PDF del listado de usuarios."""
    try:
        nombre = request.GET.get("nombre", "")
        correo = request.GET.get("correo", "")
        rol = request.GET.get("rol", "")
        estado = request.GET.get("estado", "")

        usuarios = usuario_service.listar_filtrado(nombre, correo, rol, estado)
        bloques = helper.construir_reporte(usuarios)
        pdf = crear_pdf_compuesto("Reporte de Usuarios", bloques)

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="reporte_usuarios.pdf"'
        return response
    except Exception:
        return HttpResponse("No fue posible generar el reporte de usuarios.", status=500)


def _usuario_to_dict(usuario):
    """Convierte un usuario a formato JSON simple."""
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre or "",
        "apellido": usuario.apellido or "",
        "nombre_completo": usuario.nombre_completo(),
        "correo": usuario.correo or "",
        "telefono": usuario.telefono or "",
        "tipo_usuario": usuario.tipo_usuario or "",
        "estado": usuario.estado or "",
    }


def _usuario_api_payload(usuario):
    """Agrega token API a la respuesta del usuario."""
    payload = _usuario_to_dict(usuario)
    mesa = mesa_service.mesa_por_usuario(usuario.id_usuario)
    payload["mesa_id"] = mesa.get("id") if mesa else None
    payload["mesa_label"] = f"Mesa {mesa.get('id')}" if mesa and mesa.get("id") else ""
    payload["api_token"] = emitir_api_token(usuario)
    return payload


def _leer_json_request(request):
    """Lee JSON del body de la peticion."""
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "JSON invalido"}, status=400)


@csrf_exempt
def api_registro_cliente(request):
    """Registra clientes desde la API."""
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    data, error = _leer_json_request(request)
    if error:
        return error

    nombre_completo = (data.get("nombre") or "").strip()
    correo = (data.get("correo") or "").strip().lower()
    clave = data.get("clave") or ""
    telefono = (data.get("telefono") or "").strip()

    if not nombre_completo or not correo or not clave:
        return JsonResponse(
            {"error": "Nombre, correo y clave son obligatorios"},
            status=400,
        )

    clave_valida, error_clave = validar_contrasena_segura(clave)
    if not clave_valida:
        return JsonResponse({"error": error_clave}, status=400)

    if usuario_service.buscar_por_correo(correo):
        return JsonResponse({"error": "El correo ya esta registrado"}, status=400)

    partes = nombre_completo.split()
    nombre = partes[0]
    apellido = " ".join(partes[1:]) if len(partes) > 1 else ""

    usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        correo=correo,
        clave=hash_contrasena(clave),
        telefono=telefono,
        tipo_usuario="cliente",
        estado="Activo",
    )
    usuario_service.guardar(usuario)
    return JsonResponse(_usuario_api_payload(usuario), status=201)


@csrf_exempt
def api_login_cliente(request):
    """Permite login de clientes por API."""
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    data, error = _leer_json_request(request)
    if error:
        return error

    correo = (data.get("correo") or "").strip().lower()
    clave = data.get("clave") or ""
    usuario = usuario_service.autenticar(correo, clave)

    if not usuario:
        return JsonResponse({"error": "Correo o clave incorrectos"}, status=401)

    return JsonResponse(_usuario_api_payload(usuario))


@csrf_exempt
def api_login_mesero(request):
    """Permite login de usuarios tipo mesero por API."""
    if request.method != "POST":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    data, error = _leer_json_request(request)
    if error:
        return error

    correo = (data.get("correo") or "").strip().lower()
    clave = data.get("clave") or ""
    usuario = usuario_service.autenticar(correo, clave)

    if not usuario:
        return JsonResponse({"error": "Correo o clave incorrectos"}, status=401)

    es_mesero = (usuario.tipo_usuario or "").strip().lower() == "mesero"
    rol_nombre = (usuario.get_rol_nombre() or "").strip().lower()

    if not es_mesero and "mesero" not in rol_nombre:
        return JsonResponse(
            {"error": "Solo usuarios tipo mesero pueden ingresar aqui"},
            status=403,
        )

    return JsonResponse(_usuario_api_payload(usuario))


@csrf_exempt
def api_refresh_session(request):
    """Entrega un token nuevo para la sesion actual."""
    from bongusto.modules.shared.api_auth import resolver_usuario_api

    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    usuario, _, error = resolver_usuario_api(request)
    if error:
        return error

    return JsonResponse(_usuario_api_payload(usuario))
