"""Estado real de mesas basado en una sola maquina de estados."""

from django.core.cache import cache
from django.db import connection
from django.utils import timezone

from bongusto.domain.models import Bitacora, PedidoEncabezado, Reserva, SolicitudPago
from bongusto.modules.mesas.models import Mesa


class MesaStateService:
    """Administra mesas reales y evita estados duplicados entre Django y Flutter."""

    ESTADOS_PERMITIDOS = {
        Mesa.ESTADO_LIBRE,
        Mesa.ESTADO_OCUPADA,
        Mesa.ESTADO_ESPERANDO_PAGO,
        Mesa.ESTADO_PAGADA,
        Mesa.ESTADO_EN_LIMPIEZA,
        Mesa.ESTADO_BLOQUEADA,
    }
    LEGACY_STATE_MAP = {
        "disponible": Mesa.ESTADO_LIBRE,
        "ocupada": Mesa.ESTADO_OCUPADA,
        "reservada": Mesa.ESTADO_BLOQUEADA,
        "pendiente_pago": Mesa.ESTADO_ESPERANDO_PAGO,
        "inactiva": Mesa.ESTADO_BLOQUEADA,
        "deshabilitada": Mesa.ESTADO_BLOQUEADA,
        "bloqueada": Mesa.ESTADO_BLOQUEADA,
        "libre": Mesa.ESTADO_LIBRE,
        "esperando_pago": Mesa.ESTADO_ESPERANDO_PAGO,
        "pagada": Mesa.ESTADO_PAGADA,
        "en_limpieza": Mesa.ESTADO_EN_LIMPIEZA,
    }

    def __init__(self):
        self._schema_ready = False

    def asegurar_esquema(self):
        """Crea columnas faltantes y normaliza valores legados."""
        if self._schema_ready:
            return

        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE 'mesas'")
            existe_mesas = cursor.fetchone()
            if not existe_mesas:
                cursor.execute(
                    """
                    CREATE TABLE mesas (
                        id_mesa INT AUTO_INCREMENT PRIMARY KEY,
                        numero_mesa INT NOT NULL,
                        nombre VARCHAR(120) NULL,
                        capacidad INT NOT NULL DEFAULT 2,
                        estado VARCHAR(20) NOT NULL DEFAULT 'libre',
                        activa TINYINT(1) NOT NULL DEFAULT 1,
                        id_usuario_actual INT NULL,
                        id_pedido_actual INT NULL,
                        id_mesero_asignado INT NULL,
                        fecha_ocupacion DATETIME(6) NULL,
                        fecha_solicitud_pago DATETIME(6) NULL,
                        fecha_pago DATETIME(6) NULL,
                        fecha_liberacion DATETIME(6) NULL,
                        fecha_creacion DATETIME(6) NOT NULL,
                        fecha_actualizacion DATETIME(6) NOT NULL,
                        asignado_en DATETIME(6) NULL,
                        UNIQUE KEY mesas_numero_unq (numero_mesa),
                        KEY mesas_activa_idx (activa),
                        KEY mesas_estado_idx (estado),
                        KEY mesas_usuario_actual_idx (id_usuario_actual),
                        KEY mesas_pedido_actual_idx (id_pedido_actual),
                        KEY mesas_mesero_asignado_idx (id_mesero_asignado)
                    )
                    """
                )
            else:
                self._asegurar_columna(cursor, "mesas", "nombre", "VARCHAR(120) NULL")
                self._asegurar_columna(cursor, "mesas", "capacidad", "INT NOT NULL DEFAULT 2")
                self._asegurar_columna(cursor, "mesas", "estado", "VARCHAR(20) NOT NULL DEFAULT 'libre'")
                self._asegurar_columna(cursor, "mesas", "activa", "TINYINT(1) NOT NULL DEFAULT 1")
                self._asegurar_columna(cursor, "mesas", "id_usuario_actual", "INT NULL")
                self._asegurar_columna(cursor, "mesas", "id_pedido_actual", "INT NULL")
                self._asegurar_columna(cursor, "mesas", "id_mesero_asignado", "INT NULL")
                self._asegurar_columna(cursor, "mesas", "fecha_ocupacion", "DATETIME(6) NULL")
                self._asegurar_columna(cursor, "mesas", "fecha_solicitud_pago", "DATETIME(6) NULL")
                self._asegurar_columna(cursor, "mesas", "fecha_pago", "DATETIME(6) NULL")
                self._asegurar_columna(cursor, "mesas", "fecha_liberacion", "DATETIME(6) NULL")
                self._asegurar_columna(cursor, "mesas", "fecha_creacion", "DATETIME(6) NULL")
                self._asegurar_columna(cursor, "mesas", "fecha_actualizacion", "DATETIME(6) NULL")
                self._asegurar_columna(cursor, "mesas", "asignado_en", "DATETIME(6) NULL")
                self._asegurar_indice(cursor, "mesas", "mesas_activa_idx", "CREATE INDEX mesas_activa_idx ON mesas(activa)")
                self._asegurar_indice(cursor, "mesas", "mesas_estado_idx", "CREATE INDEX mesas_estado_idx ON mesas(estado)")
                self._asegurar_indice(cursor, "mesas", "mesas_usuario_actual_idx", "CREATE INDEX mesas_usuario_actual_idx ON mesas(id_usuario_actual)")
                self._asegurar_indice(cursor, "mesas", "mesas_pedido_actual_idx", "CREATE INDEX mesas_pedido_actual_idx ON mesas(id_pedido_actual)")
                self._asegurar_indice(cursor, "mesas", "mesas_mesero_asignado_idx", "CREATE INDEX mesas_mesero_asignado_idx ON mesas(id_mesero_asignado)")

            cursor.execute(
                """
                UPDATE mesas
                SET
                    estado = CASE
                        WHEN estado IN ('disponible', 'libre', '') OR estado IS NULL THEN 'libre'
                        WHEN estado IN ('pendiente_pago', 'esperando_pago') THEN 'esperando_pago'
                        WHEN estado IN ('inactiva', 'deshabilitada', 'bloqueada', 'reservada') THEN 'bloqueada'
                        WHEN estado IN ('pagada') THEN 'pagada'
                        WHEN estado IN ('en_limpieza') THEN 'en_limpieza'
                        ELSE 'ocupada'
                    END,
                    capacidad = CASE WHEN capacidad IS NULL OR capacidad <= 0 THEN 2 ELSE capacidad END,
                    activa = CASE WHEN activa IS NULL THEN 1 WHEN estado = 'bloqueada' THEN 0 ELSE activa END,
                    fecha_creacion = COALESCE(fecha_creacion, NOW(6)),
                    fecha_actualizacion = COALESCE(fecha_actualizacion, NOW(6))
                """
            )

        self._sembrar_mesas_base_si_hace_falta()
        self._schema_ready = True

    def _asegurar_columna(self, cursor, tabla, columna, definicion):
        cursor.execute(f"SHOW COLUMNS FROM {tabla} LIKE '{columna}'")
        if cursor.fetchone():
            return
        cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")

    def _asegurar_indice(self, cursor, tabla, indice, sentencia_create):
        cursor.execute(f"SHOW INDEX FROM {tabla} WHERE Key_name = '{indice}'")
        if cursor.fetchone():
            return
        cursor.execute(sentencia_create)

    def _sembrar_mesas_base_si_hace_falta(self):
        if Mesa.objects.exists():
            return

        numeros = set()
        numeros.update(
            int(item)
            for item in PedidoEncabezado.objects.exclude(mesa_id__isnull=True).values_list("mesa_id", flat=True)
            if int(item or 0) > 0
        )
        numeros.update(
            int(item)
            for item in Reserva.objects.exclude(mesa_id__isnull=True).values_list("mesa_id", flat=True)
            if int(item or 0) > 0
        )
        numeros.update(
            int(item)
            for item in SolicitudPago.objects.exclude(mesa_id__isnull=True).values_list("mesa_id", flat=True)
            if int(item or 0) > 0
        )
        if not numeros:
            return

        ahora = timezone.now()
        Mesa.objects.bulk_create(
            [
                Mesa(
                    numero_mesa=numero,
                    nombre="",
                    capacidad=4,
                    estado=Mesa.ESTADO_LIBRE,
                    activa=True,
                    fecha_creacion=ahora,
                    fecha_actualizacion=ahora,
                )
                for numero in sorted(numeros)
            ]
        )

    def normalizar_estado(self, estado):
        valor = (estado or "").strip().lower()
        return self.LEGACY_STATE_MAP.get(valor, valor)

    def listar_modelos(self, incluir_inactivas=True):
        self.asegurar_esquema()
        qs = Mesa.objects.select_related(
            "usuario_actual",
            "pedido_actual",
            "mesero_asignado",
        ).order_by("numero_mesa", "id")
        if not incluir_inactivas:
            qs = qs.filter(activa=True)
        mesas = list(qs)
        for mesa in mesas:
            self._sincronizar_mesa(mesa)
        return mesas

    def listar(self, incluir_inactivas=True):
        return [self._mesa_payload(mesa) for mesa in self.listar_modelos(incluir_inactivas=incluir_inactivas)]

    def buscar_modelo(self, mesa_id):
        self.asegurar_esquema()
        mesa = (
            Mesa.objects.select_related("usuario_actual", "pedido_actual", "mesero_asignado")
            .filter(pk=mesa_id)
            .first()
        )
        if mesa:
            self._sincronizar_mesa(mesa)
        return mesa

    def buscar_por_numero(self, numero_mesa):
        self.asegurar_esquema()
        mesa = (
            Mesa.objects.select_related("usuario_actual", "pedido_actual", "mesero_asignado")
            .filter(numero_mesa=numero_mesa)
            .first()
        )
        if mesa:
            self._sincronizar_mesa(mesa)
        return mesa

    def detalle(self, mesa_id):
        mesa = self.buscar_modelo(mesa_id)
        if not mesa:
            return None
        return self._mesa_payload(mesa)

    def mesa_por_usuario(self, usuario_id):
        self.asegurar_esquema()
        if not usuario_id:
            return None
        mesa = (
            Mesa.objects.select_related("usuario_actual", "pedido_actual", "mesero_asignado")
            .filter(usuario_actual_id=usuario_id)
            .order_by("numero_mesa", "id")
            .first()
        )
        if not mesa:
            return None
        self._sincronizar_mesa(mesa)
        return self._mesa_payload(mesa)

    def seleccionar_para_cliente(self, usuario, *, mesa_id=None, numero_mesa=None):
        self.asegurar_esquema()
        if not usuario:
            raise ValueError("Usuario no valido.")

        actual = Mesa.objects.filter(usuario_actual=usuario).first()
        if actual:
            self._sincronizar_mesa(actual)
            if not mesa_id and not numero_mesa and actual.estado != Mesa.ESTADO_BLOQUEADA:
                return actual
            if (
                (mesa_id and int(actual.id) == int(mesa_id))
                or (numero_mesa and int(actual.numero_mesa) == int(numero_mesa))
            ) and actual.estado != Mesa.ESTADO_BLOQUEADA:
                return actual
            if actual.pedido_actual_id or self._pago_activo(actual):
                raise ValueError("No puedes cambiar de mesa mientras tengas un pedido o pago activo.")
            actual.usuario_actual = None
            actual.asignado_en = None
            actual.fecha_ocupacion = None
            actual.estado = Mesa.ESTADO_LIBRE
            actual.save(
                update_fields=[
                    "usuario_actual",
                    "asignado_en",
                    "fecha_ocupacion",
                    "estado",
                    "fecha_actualizacion",
                ]
            )

        mesa = None
        if mesa_id:
            mesa = self.buscar_modelo(mesa_id)
        elif numero_mesa:
            mesa = self.buscar_por_numero(numero_mesa)

        if not mesa:
            raise ValueError("La mesa indicada no existe.")
        if not mesa.activa or mesa.estado == Mesa.ESTADO_BLOQUEADA:
            raise ValueError("La mesa no esta disponible.")
        if mesa.estado in {Mesa.ESTADO_OCUPADA, Mesa.ESTADO_ESPERANDO_PAGO, Mesa.ESTADO_PAGADA, Mesa.ESTADO_EN_LIMPIEZA}:
            if mesa.usuario_actual_id != usuario.id_usuario:
                raise ValueError("La mesa ya esta en uso.")

        mesa.usuario_actual = usuario
        mesa.fecha_ocupacion = mesa.fecha_ocupacion or timezone.now()
        mesa.asignado_en = mesa.fecha_ocupacion
        mesa.fecha_liberacion = None
        if mesa.estado == Mesa.ESTADO_LIBRE:
            mesa.estado = Mesa.ESTADO_OCUPADA
        mesa.activa = True
        mesa.save(
            update_fields=[
                "usuario_actual",
                "fecha_ocupacion",
                "asignado_en",
                "fecha_liberacion",
                "estado",
                "activa",
                "fecha_actualizacion",
            ]
        )
        return mesa

    def ocupar_con_pedido(self, mesa, pedido, *, cliente=None):
        mesa = mesa if isinstance(mesa, Mesa) else self.buscar_modelo(mesa)
        if not mesa:
            raise ValueError("Mesa no encontrada.")
        if not mesa.activa or mesa.estado == Mesa.ESTADO_BLOQUEADA:
            raise ValueError("La mesa no esta disponible para pedidos.")
        if mesa.pedido_actual_id and mesa.pedido_actual_id != pedido.id_pedido:
            raise ValueError("La mesa ya tiene un pedido activo.")

        mesa.pedido_actual = pedido
        if cliente:
            mesa.usuario_actual = cliente
        mesa.estado = Mesa.ESTADO_OCUPADA
        mesa.fecha_ocupacion = mesa.fecha_ocupacion or timezone.now()
        mesa.asignado_en = mesa.fecha_ocupacion
        mesa.fecha_solicitud_pago = None
        mesa.fecha_pago = None
        mesa.fecha_liberacion = None
        mesa.activa = True
        mesa.save(
            update_fields=[
                "pedido_actual",
                "usuario_actual",
                "estado",
                "fecha_ocupacion",
                "asignado_en",
                "fecha_solicitud_pago",
                "fecha_pago",
                "fecha_liberacion",
                "activa",
                "fecha_actualizacion",
            ]
        )
        return mesa

    def registrar_solicitud_pago(self, mesa, solicitud):
        mesa = mesa if isinstance(mesa, Mesa) else self.buscar_modelo(mesa)
        if not mesa:
            raise ValueError("Mesa no encontrada.")
        if not mesa.pedido_actual_id and not solicitud.id_pedido_id:
            raise ValueError("La mesa no tiene pedido activo.")

        if solicitud.id_pedido_id and not mesa.pedido_actual_id:
            mesa.pedido_actual = solicitud.id_pedido
        mesa.estado = Mesa.ESTADO_ESPERANDO_PAGO
        mesa.fecha_solicitud_pago = timezone.now()
        mesa.fecha_pago = None
        mesa.save(
            update_fields=[
                "pedido_actual",
                "estado",
                "fecha_solicitud_pago",
                "fecha_pago",
                "fecha_actualizacion",
            ]
        )
        return mesa

    def confirmar_pago(self, mesa, *, solicitud=None, mesero=None):
        mesa = mesa if isinstance(mesa, Mesa) else self.buscar_modelo(mesa)
        if not mesa:
            raise ValueError("Mesa no encontrada.")
        if mesa.estado not in {Mesa.ESTADO_ESPERANDO_PAGO, Mesa.ESTADO_OCUPADA}:
            raise ValueError("La mesa no tiene un pago pendiente por confirmar.")

        self._finalizar_pedido_activo(mesa, solicitud=solicitud)
        mesa.estado = Mesa.ESTADO_PAGADA
        mesa.mesero_asignado = mesero if getattr(mesero, "id_usuario", None) else mesa.mesero_asignado
        mesa.fecha_pago = timezone.now()
        if solicitud and solicitud.id_pedido_id and not mesa.pedido_actual_id:
            mesa.pedido_actual = solicitud.id_pedido
        mesa.save(
            update_fields=[
                "estado",
                "mesero_asignado",
                "fecha_pago",
                "pedido_actual",
                "fecha_actualizacion",
            ]
        )
        return mesa

    def marcar_en_limpieza(self, mesa, *, mesero=None):
        mesa = mesa if isinstance(mesa, Mesa) else self.buscar_modelo(mesa)
        if not mesa:
            raise ValueError("Mesa no encontrada.")
        if mesa.estado not in {Mesa.ESTADO_PAGADA, Mesa.ESTADO_OCUPADA, Mesa.ESTADO_ESPERANDO_PAGO}:
            raise ValueError("La mesa no puede pasar a limpieza en este momento.")

        mesa.estado = Mesa.ESTADO_EN_LIMPIEZA
        if getattr(mesero, "id_usuario", None):
            mesa.mesero_asignado = mesero
        mesa.save(update_fields=["estado", "mesero_asignado", "fecha_actualizacion"])
        return mesa

    def liberar(self, mesa, *, forzada=False, mesero=None):
        mesa = mesa if isinstance(mesa, Mesa) else self.buscar_modelo(mesa)
        if not mesa:
            raise ValueError("Mesa no encontrada.")

        pago_activo = self._pago_activo(mesa)
        if pago_activo and pago_activo.estado != "finalizada":
            if not forzada:
                raise ValueError("No se puede liberar una mesa con pago pendiente.")
            self._cerrar_pagos_activos(
                mesa,
                notas="Cierre operativo por liberacion forzada de mesa.",
                atendido_por=getattr(mesero, "id_usuario", None),
            )
            self._finalizar_pedido_activo(mesa, solicitud=pago_activo)

        if mesa.estado == Mesa.ESTADO_BLOQUEADA and not forzada:
            raise ValueError("La mesa esta bloqueada.")

        if mesa.estado != Mesa.ESTADO_EN_LIMPIEZA:
            mesa.estado = Mesa.ESTADO_EN_LIMPIEZA
            mesa.save(update_fields=["estado", "fecha_actualizacion"])

        mesa.estado = Mesa.ESTADO_LIBRE
        mesa.usuario_actual = None
        mesa.pedido_actual = None
        mesa.mesero_asignado = None
        mesa.fecha_liberacion = timezone.now()
        mesa.asignado_en = None
        mesa.fecha_ocupacion = None
        mesa.fecha_solicitud_pago = None
        mesa.fecha_pago = None
        mesa.save(
            update_fields=[
                "estado",
                "usuario_actual",
                "pedido_actual",
                "mesero_asignado",
                "fecha_liberacion",
                "asignado_en",
                "fecha_ocupacion",
                "fecha_solicitud_pago",
                "fecha_pago",
                "fecha_actualizacion",
            ]
        )
        return mesa

    def limpiar_cache_operacion(self):
        """Limpia cache global y reconstruye el estado operativo de todas las mesas."""
        cache.clear()
        self._schema_ready = False
        self.asegurar_esquema()
        mesas = self.listar_modelos(incluir_inactivas=True)
        for mesa in mesas:
            self._sincronizar_mesa(mesa)
        return [self._mesa_payload(mesa) for mesa in mesas]

    def bloquear(self, mesa, *, motivo=""):
        mesa = mesa if isinstance(mesa, Mesa) else self.buscar_modelo(mesa)
        if not mesa:
            raise ValueError("Mesa no encontrada.")
        if mesa.estado != Mesa.ESTADO_LIBRE:
            raise ValueError("No se puede bloquear una mesa con un proceso activo.")

        mesa.estado = Mesa.ESTADO_BLOQUEADA
        mesa.activa = False
        mesa.save(update_fields=["estado", "activa", "fecha_actualizacion"])
        return mesa

    def reactivar(self, mesa):
        mesa = mesa if isinstance(mesa, Mesa) else self.buscar_modelo(mesa)
        if not mesa:
            raise ValueError("Mesa no encontrada.")
        if mesa.pedido_actual_id:
            raise ValueError("No se puede reactivar una mesa con pedido activo.")
        if self._pago_activo(mesa):
            raise ValueError("No se puede reactivar una mesa con pago pendiente.")

        mesa.activa = True
        mesa.estado = Mesa.ESTADO_LIBRE
        mesa.usuario_actual = None
        mesa.asignado_en = None
        mesa.fecha_ocupacion = None
        mesa.fecha_solicitud_pago = None
        mesa.fecha_pago = None
        mesa.fecha_liberacion = timezone.now()
        mesa.save(
            update_fields=[
                "activa",
                "estado",
                "usuario_actual",
                "asignado_en",
                "fecha_ocupacion",
                "fecha_solicitud_pago",
                "fecha_pago",
                "fecha_liberacion",
                "fecha_actualizacion",
            ]
        )
        return mesa

    def actualizar_estado(self, mesa_id, estado):
        """Compatibilidad para acciones legadas; usa transiciones canonicas."""
        mesa = self.buscar_modelo(mesa_id)
        if not mesa:
            return None

        estado = self.normalizar_estado(estado)
        if estado == Mesa.ESTADO_LIBRE:
            return self.liberar(mesa)
        if estado == Mesa.ESTADO_ESPERANDO_PAGO:
            mesa.estado = Mesa.ESTADO_ESPERANDO_PAGO
            mesa.fecha_solicitud_pago = timezone.now()
            mesa.save(update_fields=["estado", "fecha_solicitud_pago", "fecha_actualizacion"])
            return mesa
        if estado == Mesa.ESTADO_PAGADA:
            mesa.estado = Mesa.ESTADO_PAGADA
            mesa.fecha_pago = timezone.now()
            mesa.save(update_fields=["estado", "fecha_pago", "fecha_actualizacion"])
            return mesa
        if estado == Mesa.ESTADO_EN_LIMPIEZA:
            return self.marcar_en_limpieza(mesa)
        if estado == Mesa.ESTADO_BLOQUEADA:
            return self.bloquear(mesa)
        if estado == Mesa.ESTADO_OCUPADA:
            mesa.estado = Mesa.ESTADO_OCUPADA
            mesa.activa = True
            mesa.fecha_ocupacion = mesa.fecha_ocupacion or timezone.now()
            mesa.asignado_en = mesa.fecha_ocupacion
            mesa.save(update_fields=["estado", "activa", "fecha_ocupacion", "asignado_en", "fecha_actualizacion"])
            return mesa
        return None

    def puede_desactivar(self, mesa):
        mesa = mesa if isinstance(mesa, Mesa) else self.buscar_modelo(mesa)
        if not mesa:
            return False, "Mesa no valida."
        self._sincronizar_mesa(mesa)
        if mesa.estado != Mesa.ESTADO_LIBRE:
            return False, "No se puede quitar esta mesa porque tiene un proceso activo."
        if mesa.pedido_actual_id:
            return False, "No se puede quitar esta mesa porque tiene un pedido activo."
        if self._pago_activo(mesa):
            return False, "No se puede quitar esta mesa porque tiene un pago activo."
        return True, ""

    def puede_eliminar(self, mesa):
        return self.puede_desactivar(mesa)

    def tiene_historial(self, mesa):
        mesa_id = getattr(mesa, "id", mesa)
        if not mesa_id:
            return False
        return (
            PedidoEncabezado.objects.filter(mesa_id=mesa_id).exists()
            or Reserva.objects.filter(mesa_id=mesa_id).exists()
            or SolicitudPago.objects.filter(mesa_id=mesa_id).exists()
            or Bitacora.objects.filter(accion__icontains=f"mesa {mesa_id}").exists()
        )

    def eliminar_o_desactivar(self, mesa):
        mesa = mesa if isinstance(mesa, Mesa) else self.buscar_modelo(mesa)
        permitido, motivo = self.puede_desactivar(mesa)
        if not permitido:
            return False, motivo

        if self.tiene_historial(mesa):
            return (
                True,
                "Mesa con actividad histórica. El sistema recomienda desactivarla para conservar el historial, pero si confirmas se eliminara definitivamente.",
            )

        mesa.delete()
        return True, "Mesa eliminada."

    def historial(self, mesa_id):
        mesa = self.buscar_modelo(mesa_id)
        if not mesa:
            return None

        pedidos = [
            {
                "id_pedido": pedido.id_pedido,
                "id_usuario": pedido.id_usuario_id,
                "fecha_pedido": str(pedido.fecha_pedido) if pedido.fecha_pedido else "",
                "total_pedido": float(pedido.total_pedido or 0),
            }
            for pedido in PedidoEncabezado.objects.filter(mesa_id=mesa.id).order_by("-id_pedido")[:50]
        ]
        pagos = [
            {
                "id_solicitud_pago": pago.id_solicitud_pago,
                "estado": pago.estado,
                "metodo_pago": pago.metodo_pago,
                "fecha_creacion": pago.fecha_creacion.isoformat() if pago.fecha_creacion else "",
                "finalizado_en": pago.finalizado_en.isoformat() if pago.finalizado_en else "",
            }
            for pago in SolicitudPago.objects.filter(mesa_id=mesa.id).order_by("-fecha_creacion")[:50]
        ]
        movimientos = [
            {
                "id_log": item.id_log,
                "accion": item.accion or "",
                "fecha_accion": item.fecha_accion.isoformat() if item.fecha_accion else "",
            }
            for item in Bitacora.objects.filter(accion__icontains=f"mesa {mesa.numero_mesa}").order_by("-fecha_accion")[:80]
        ]
        return {
            "mesa": self._mesa_payload(mesa),
            "pedidos": pedidos,
            "pagos": pagos,
            "movimientos": movimientos,
        }

    def _reserva_activa(self, mesa):
        hoy = timezone.localdate()
        return (
            Reserva.objects.filter(mesa_id=mesa.id, estado_reser__iexact="activa", fecha_reser__gte=hoy)
            .order_by("fecha_reser", "hora_reser")
            .first()
        )

    def _pago_activo(self, mesa):
        return (
            SolicitudPago.objects.select_related("id_usuario", "id_pedido", "atendido_por")
            .filter(mesa_id=mesa.id)
            .exclude(estado="finalizada")
            .order_by("-fecha_creacion")
            .first()
        )

    def _cerrar_pagos_activos(self, mesa, *, notas="", atendido_por=None):
        ahora = timezone.now()
        solicitudes = SolicitudPago.objects.filter(mesa_id=mesa.id).exclude(estado="finalizada")
        for solicitud in solicitudes:
            solicitud.estado = "finalizada"
            solicitud.finalizado_en = solicitud.finalizado_en or ahora
            if notas:
                solicitud.notas = (f"{(solicitud.notas or '').strip()} {notas}").strip()
            if atendido_por:
                solicitud.atendido_por_id = atendido_por
            solicitud.save(
                update_fields=[
                    "estado",
                    "finalizado_en",
                    "notas",
                    "atendido_por",
                    "fecha_actualizacion",
                ]
            )

    def _finalizar_pedido_activo(self, mesa, *, solicitud=None):
        pedido = getattr(mesa, "pedido_actual", None)
        if not pedido and solicitud and getattr(solicitud, "id_pedido_id", None):
            pedido = solicitud.id_pedido
        if not pedido:
            pedido = (
                PedidoEncabezado.objects.select_related("id_usuario")
                .filter(mesa_id=mesa.id)
                .exclude(estado_pedido="finalizado")
                .order_by("-id_pedido")
                .first()
            )
        if not pedido or getattr(pedido, "estado_pedido", "abierto") == "finalizado":
            return None

        pedido.estado_pedido = "finalizado"
        pedido.fecha_finalizacion = timezone.now()
        pedido.save(update_fields=["estado_pedido", "fecha_finalizacion"])
        return pedido

    def _pedidos_relacionados(self, mesa):
        return list(
            PedidoEncabezado.objects.select_related("id_usuario")
            .prefetch_related("pedidodetalle_set")
            .filter(mesa_id=mesa.id)
            .order_by("-id_pedido")[:20]
        )

    def _sincronizar_mesa(self, mesa):
        """Alinea los campos operativos de la mesa con el proceso real en Django."""
        cambios = []
        reserva = self._reserva_activa(mesa)
        pago = self._pago_activo(mesa)

        if not mesa.pedido_actual_id:
            pedido_rel = (
                PedidoEncabezado.objects.select_related("id_usuario")
                .filter(mesa_id=mesa.id)
                .exclude(estado_pedido="finalizado")
                .order_by("-id_pedido")
                .first()
            )
            if (
                not pedido_rel
                and mesa.usuario_actual_id
                and mesa.estado in {Mesa.ESTADO_OCUPADA, Mesa.ESTADO_ESPERANDO_PAGO, Mesa.ESTADO_PAGADA, Mesa.ESTADO_EN_LIMPIEZA}
            ):
                pedido_rel = (
                    PedidoEncabezado.objects.select_related("id_usuario")
                    .filter(id_usuario_id=mesa.usuario_actual_id)
                    .exclude(estado_pedido="finalizado")
                    .order_by("-id_pedido")
                    .first()
                )
                if pedido_rel and pedido_rel.mesa_id != mesa.id:
                    pedido_rel.mesa = mesa
                    pedido_rel.save(update_fields=["mesa"])
            if pedido_rel and mesa.estado in {Mesa.ESTADO_OCUPADA, Mesa.ESTADO_ESPERANDO_PAGO, Mesa.ESTADO_PAGADA, Mesa.ESTADO_EN_LIMPIEZA}:
                mesa.pedido_actual = pedido_rel
                cambios.append("pedido_actual")

        if not mesa.activa:
            if mesa.estado != Mesa.ESTADO_BLOQUEADA:
                mesa.estado = Mesa.ESTADO_BLOQUEADA
                cambios.append("estado")
        elif pago:
            if mesa.estado != Mesa.ESTADO_ESPERANDO_PAGO:
                mesa.estado = Mesa.ESTADO_ESPERANDO_PAGO
                cambios.append("estado")
            if not mesa.fecha_solicitud_pago:
                mesa.fecha_solicitud_pago = pago.fecha_creacion
                cambios.append("fecha_solicitud_pago")
        elif mesa.estado == Mesa.ESTADO_PAGADA and mesa.pedido_actual_id:
            pass
        elif mesa.estado == Mesa.ESTADO_EN_LIMPIEZA:
            pass
        elif mesa.pedido_actual_id or mesa.usuario_actual_id:
            if mesa.estado != Mesa.ESTADO_OCUPADA:
                mesa.estado = Mesa.ESTADO_OCUPADA
                cambios.append("estado")
        elif reserva:
            if mesa.estado != Mesa.ESTADO_BLOQUEADA:
                mesa.estado = Mesa.ESTADO_BLOQUEADA
                cambios.append("estado")
        else:
            if mesa.estado != Mesa.ESTADO_LIBRE:
                mesa.estado = Mesa.ESTADO_LIBRE
                cambios.append("estado")
            if mesa.usuario_actual_id:
                mesa.usuario_actual = None
                cambios.append("usuario_actual")
            if mesa.pedido_actual_id:
                mesa.pedido_actual = None
                cambios.append("pedido_actual")
            if mesa.mesero_asignado_id:
                mesa.mesero_asignado = None
                cambios.append("mesero_asignado")

        if mesa.estado == Mesa.ESTADO_LIBRE:
            if mesa.asignado_en is not None:
                mesa.asignado_en = None
                cambios.append("asignado_en")
            if mesa.fecha_ocupacion is not None:
                mesa.fecha_ocupacion = None
                cambios.append("fecha_ocupacion")
            if mesa.fecha_solicitud_pago is not None:
                mesa.fecha_solicitud_pago = None
                cambios.append("fecha_solicitud_pago")
            if mesa.fecha_pago is not None:
                mesa.fecha_pago = None
                cambios.append("fecha_pago")

        if cambios:
            cambios.append("fecha_actualizacion")
            mesa.save(update_fields=list(dict.fromkeys(cambios)))
        return mesa

    def _mesa_payload(self, mesa):
        mesa = self._sincronizar_mesa(mesa)
        pedidos = self._pedidos_relacionados(mesa)
        pago = self._pago_activo(mesa)
        reserva = self._reserva_activa(mesa)
        cliente = mesa.usuario_actual
        pedido_actual = mesa.pedido_actual or (pedidos[0] if pedidos else None)
        mesero = mesa.mesero_asignado

        return {
            "id": mesa.id,
            "numero_mesa": mesa.numero_mesa,
            "nombre": mesa.nombre or "",
            "etiqueta": mesa.etiqueta,
            "mesa_label": mesa.etiqueta,
            "capacidad": mesa.capacidad,
            "estado": mesa.estado,
            "activo": mesa.activa,
            "activa": mesa.activa,
            "pedido_actual": pedido_actual.id_pedido if pedido_actual else None,
            "pedido_actual_id": pedido_actual.id_pedido if pedido_actual else None,
            "pedido_actual_estado": getattr(pedido_actual, "estado_pedido", None) if pedido_actual else None,
            "cliente_actual": cliente.id_usuario if cliente else None,
            "cliente_id": cliente.id_usuario if cliente else None,
            "id_usuario": cliente.id_usuario if cliente else None,
            "cliente_nombre": cliente.nombre_completo() if cliente else "",
            "cliente_correo": cliente.correo if cliente else "",
            "mesero_asignado": mesero.id_usuario if mesero else None,
            "mesero_asignado_nombre": mesero.nombre_completo() if mesero else "",
            "fecha_ocupacion": mesa.fecha_ocupacion.isoformat() if mesa.fecha_ocupacion else None,
            "fecha_solicitud_pago": mesa.fecha_solicitud_pago.isoformat() if mesa.fecha_solicitud_pago else None,
            "fecha_pago": mesa.fecha_pago.isoformat() if mesa.fecha_pago else None,
            "fecha_liberacion": mesa.fecha_liberacion.isoformat() if mesa.fecha_liberacion else None,
            "created_at": mesa.fecha_creacion.isoformat() if mesa.fecha_creacion else None,
            "updated_at": mesa.fecha_actualizacion.isoformat() if mesa.fecha_actualizacion else None,
            "asignado_en": mesa.asignado_en.isoformat() if mesa.asignado_en else None,
            "pago": {
                "id_solicitud_pago": pago.id_solicitud_pago,
                "estado": pago.estado,
                "metodo_pago": pago.metodo_pago,
                "id_pedido": pago.id_pedido_id,
                "id_usuario": pago.id_usuario_id,
            }
            if pago
            else None,
            "reserva": {
                "id_reser": reserva.id_reser,
                "fecha_reser": str(reserva.fecha_reser) if reserva.fecha_reser else "",
                "hora_reser": reserva.hora_reser or "",
                "nombre_evento": reserva.nombre_evento or "",
            }
            if reserva
            else None,
        }


__all__ = ["MesaStateService"]
