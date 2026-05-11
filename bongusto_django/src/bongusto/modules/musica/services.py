"""Servicios de cola musical, historial y reproduccion automatica."""

from datetime import timedelta

from django.core.cache import cache
from django.db import connection
from django.db.models import Count
from django.utils import timezone

from bongusto.domain.models import Musica, SolicitudMusica, Usuario
from bongusto.modules.mesas.models import Mesa
from bongusto.modules.shared.realtime import emitir_evento_operacion
from bongusto.modules.shared.table_state import MesaStateService


class MusicaService:
    """Gestiona catalogo, cola activa, historial y reproduccion automatica."""

    DEFAULT_DURATION_SECONDS = 210
    ACTIVE_STATES = ("pendiente", "reproduciendo")
    FINAL_STATES = ("reproducida", "eliminada")

    def __init__(self):
        self.mesa_service = MesaStateService()
        self._schema_ready = False
        self._ensuring_schema = False

    def asegurar_esquema(self):
        if self._schema_ready or self._ensuring_schema:
            return
        self._ensuring_schema = True
        try:
            with connection.cursor() as cursor:
                self._asegurar_columna(cursor, "solicitud_musica", "mesa_id", "INT NULL")
                self._asegurar_columna(cursor, "solicitud_musica", "cancion", "VARCHAR(150) NULL")
                self._asegurar_columna(cursor, "solicitud_musica", "artista", "VARCHAR(150) NULL")
                self._asegurar_columna(cursor, "solicitud_musica", "posicion_orden", "INT NULL")
                self._asegurar_columna(cursor, "solicitud_musica", "duracion_segundos", "INT NULL")
                self._asegurar_columna(cursor, "solicitud_musica", "fecha_solicitud", "DATETIME(6) NULL")
                self._asegurar_columna(cursor, "solicitud_musica", "fecha_inicio_reproduccion", "DATETIME(6) NULL")
                self._asegurar_columna(cursor, "solicitud_musica", "fecha_finalizacion", "DATETIME(6) NULL")
                self._asegurar_columna(cursor, "solicitud_musica", "eliminado_por_id", "INT NULL")
                self._asegurar_columna(cursor, "solicitud_musica", "motivo_eliminacion", "LONGTEXT NULL")
                self._asegurar_estado_moderno(cursor)
                self._asegurar_indice(
                    cursor,
                    "solicitud_musica",
                    "solicitud_musica_estado_idx",
                    "CREATE INDEX solicitud_musica_estado_idx ON solicitud_musica(estado_solicitud)",
                )
                self._asegurar_indice(
                    cursor,
                    "solicitud_musica",
                    "solicitud_musica_posicion_idx",
                    "CREATE INDEX solicitud_musica_posicion_idx ON solicitud_musica(posicion_orden)",
                )
                self._asegurar_indice(
                    cursor,
                    "solicitud_musica",
                    "solicitud_musica_mesa_idx",
                    "CREATE INDEX solicitud_musica_mesa_idx ON solicitud_musica(mesa_id)",
                )
                cursor.execute(
                    """
                    UPDATE solicitud_musica sm
                    LEFT JOIN musica m ON m.id_musica = sm.id_musica
                    SET
                        sm.cancion = COALESCE(NULLIF(sm.cancion, ''), m.nombre_musica),
                        sm.artista = COALESCE(NULLIF(sm.artista, ''), m.artista_musica),
                        sm.fecha_solicitud = COALESCE(sm.fecha_solicitud, NOW(6)),
                        sm.estado_solicitud = CASE
                            WHEN sm.estado_solicitud IN ('rechazada', 'eliminada') THEN 'eliminada'
                            WHEN sm.fecha_finalizacion IS NOT NULL AND (sm.eliminado_por_id IS NOT NULL OR COALESCE(sm.motivo_eliminacion, '') <> '') THEN 'eliminada'
                            WHEN sm.estado_solicitud = 'reproducida' THEN 'reproducida'
                            WHEN sm.fecha_finalizacion IS NOT NULL THEN 'reproducida'
                            WHEN sm.estado_solicitud IN ('aprobada', 'reproduciendo') THEN 'reproduciendo'
                            ELSE 'pendiente'
                        END
                    """
                )
                cursor.execute(
                    """
                    UPDATE solicitud_musica
                    SET fecha_inicio_reproduccion = NULL
                    WHERE estado_solicitud = 'pendiente' AND fecha_finalizacion IS NULL
                    """
                )
            self._schema_ready = True
        finally:
            self._ensuring_schema = False
        self.reordenar_cola()

    def _asegurar_estado_moderno(self, cursor):
        cursor.execute("SHOW COLUMNS FROM solicitud_musica LIKE 'estado_solicitud'")
        column = cursor.fetchone()
        if not column:
            return
        current_type = (column[1] or "").lower()
        if "varchar" in current_type:
            return
        cursor.execute(
            """
            ALTER TABLE solicitud_musica
            MODIFY COLUMN estado_solicitud VARCHAR(20) NULL
            """
        )

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

    def listar_todas(self):
        return Musica.objects.all().order_by("nombre_musica", "artista_musica")

    def buscar_por_id(self, pk):
        return Musica.objects.filter(pk=pk).first()

    def buscar_usuario_por_id(self, pk):
        return Usuario.objects.filter(pk=pk).first()

    def guardar(self, musica):
        musica.save()
        return musica

    def eliminar(self, pk):
        Musica.objects.filter(pk=pk).delete()

    def _catalogo_queryset_para_solicitud(self, solicitud):
        musica = solicitud.id_musica
        if musica:
            return Musica.objects.filter(pk=musica.pk)

        cancion = (solicitud.cancion_final or "").strip()
        artista = (solicitud.artista_final or "").strip()
        if not cancion or not artista:
            return Musica.objects.none()

        return Musica.objects.filter(
            nombre_musica__iexact=cancion,
            artista_musica__iexact=artista,
        )

    def duracion_para_solicitud(self, solicitud):
        if solicitud.duracion_segundos:
            return int(solicitud.duracion_segundos)
        if solicitud.id_musica and solicitud.id_musica.duracion_musica:
            try:
                value = float(solicitud.id_musica.duracion_musica)
                if value > 0:
                    if value <= 20:
                        return int(value * 60)
                    return int(value)
            except (TypeError, ValueError):
                pass
        return self.DEFAULT_DURATION_SECONDS

    def cola_queryset(self):
        self.asegurar_esquema()
        return SolicitudMusica.objects.select_related(
            "id_usuario", "id_musica", "mesa", "eliminado_por"
        ).filter(estado_solicitud__in=self.ACTIVE_STATES)

    def historial_queryset(self):
        self.asegurar_esquema()
        return SolicitudMusica.objects.select_related(
            "id_usuario", "id_musica", "mesa", "eliminado_por"
        ).all()

    def cola_activa(self, *, usuario=None, mesa_id=None):
        self.sincronizar_reproduccion()
        qs = self.cola_queryset()
        if mesa_id:
            qs = qs.filter(mesa_id=mesa_id)
        return [self.solicitud_to_dict(item) for item in qs.order_by("posicion_orden", "id_solicitud")]

    def historial(self, *, fecha=None, periodo=None, mesa_id=None, usuario_id=None, estado=None, cancion=None):
        self.sincronizar_reproduccion()
        qs = self.historial_queryset()
        today = timezone.localdate()
        if fecha == "hoy":
            qs = qs.filter(fecha_solicitud__date=today)
        elif periodo == "semanal":
            qs = qs.filter(fecha_solicitud__date__gte=today - timedelta(days=6))
        elif periodo == "mensual":
            qs = qs.filter(fecha_solicitud__date__gte=today - timedelta(days=29))
        if mesa_id:
            qs = qs.filter(mesa_id=mesa_id)
        if usuario_id:
            qs = qs.filter(id_usuario_id=usuario_id)
        if estado:
            qs = qs.filter(estado_solicitud=(estado or "").strip().lower())
        if cancion:
            qs = qs.filter(cancion__icontains=cancion)
        return [self.solicitud_to_dict(item) for item in qs.order_by("-fecha_solicitud", "-id_solicitud")[:300]]

    def siguiente_posicion(self):
        current = (
            SolicitudMusica.objects.filter(estado_solicitud__in=self.ACTIVE_STATES)
            .aggregate(max_pos=Count("id_solicitud"))
        )
        max_pos = SolicitudMusica.objects.filter(estado_solicitud__in=self.ACTIVE_STATES).order_by("-posicion_orden").values_list("posicion_orden", flat=True).first()
        return int(max_pos or 0) + 1

    def solicitar(
        self,
        *,
        usuario,
        musica=None,
        cancion="",
        artista="",
        mesa=None,
        mesa_id=None,
        duracion_segundos=None,
    ):
        self.asegurar_esquema()
        mesa_model = mesa
        if mesa_model is None and mesa_id:
            mesa_model = Mesa.objects.filter(pk=mesa_id).first()
        if mesa_model is None and usuario:
            mesa_payload = self.mesa_service.mesa_por_usuario(usuario.id_usuario)
            mesa_model = Mesa.objects.filter(pk=mesa_payload.get("id")).first() if mesa_payload else None

        titulo = (cancion or "").strip() or (musica.nombre_musica if musica else "")
        artista_final = (artista or "").strip() or (musica.artista_musica if musica else "")
        if not titulo or not artista_final:
            raise ValueError("Debes indicar cancion y artista.")

        solicitud = SolicitudMusica.objects.create(
            id_usuario=usuario,
            id_musica=musica,
            mesa=mesa_model,
            cancion=titulo,
            artista=artista_final,
            posicion_orden=self.siguiente_posicion(),
            duracion_segundos=int(duracion_segundos or 0) or None,
            estado_solicitud="pendiente",
        )
        payload = self.solicitud_to_dict(solicitud)
        self.emitir_evento("cancion_agregada", payload)
        self.emitir_evento("orden_cola_actualizado", self.snapshot())
        self.sincronizar_reproduccion()
        return solicitud

    def eliminar_solicitud(self, solicitud_id, *, admin, motivo="Eliminada por administrador"):
        solicitud = self.historial_queryset().filter(pk=solicitud_id).first()
        if not solicitud:
            return None
        catalogo_qs = self._catalogo_queryset_para_solicitud(solicitud)
        if solicitud.id_musica_id:
            solicitud.id_musica = None
        solicitud.estado_solicitud = "eliminada"
        solicitud.eliminado_por = admin
        solicitud.motivo_eliminacion = (motivo or "").strip() or "Eliminada por administrador"
        solicitud.fecha_finalizacion = timezone.now()
        if solicitud.fecha_inicio_reproduccion is None:
            solicitud.fecha_inicio_reproduccion = solicitud.fecha_finalizacion
        solicitud.save(
            update_fields=[
                "estado_solicitud",
                "eliminado_por",
                "motivo_eliminacion",
                "fecha_finalizacion",
                "fecha_inicio_reproduccion",
                "id_musica",
            ]
        )
        catalogo_qs.delete()
        self.reordenar_cola()
        payload = self.solicitud_to_dict(solicitud)
        self.emitir_evento("cancion_eliminada", payload)
        self.emitir_evento("historial_musical_actualizado", payload)
        self.emitir_evento("orden_cola_actualizado", self.snapshot())
        self.sincronizar_reproduccion()
        return solicitud

    def mover(self, solicitud_id, direccion):
        solicitud = self.cola_queryset().filter(pk=solicitud_id, estado_solicitud="pendiente").first()
        if not solicitud:
            return None
        pending = list(self.cola_queryset().filter(estado_solicitud="pendiente").order_by("posicion_orden", "id_solicitud"))
        indices = {item.id_solicitud: index for index, item in enumerate(pending)}
        current_index = indices.get(solicitud.id_solicitud)
        if current_index is None:
            return None
        target_index = current_index - 1 if direccion == "up" else current_index + 1
        if target_index < 0 or target_index >= len(pending):
            return solicitud
        pending[current_index], pending[target_index] = pending[target_index], pending[current_index]
        for position, item in enumerate(pending, start=2):
            item.posicion_orden = position
        SolicitudMusica.objects.bulk_update(pending, ["posicion_orden"])
        self.reordenar_cola()
        actualizado = self.historial_queryset().filter(pk=solicitud_id).first()
        self.emitir_evento("orden_cola_actualizado", self.snapshot())
        return actualizado

    def saltar(self, solicitud_id, *, admin=None):
        solicitud = self.historial_queryset().filter(pk=solicitud_id).first()
        if not solicitud:
            return None
        ahora = timezone.now()
        solicitud.estado_solicitud = "reproducida"
        solicitud.fecha_inicio_reproduccion = solicitud.fecha_inicio_reproduccion or ahora
        solicitud.fecha_finalizacion = ahora
        solicitud.motivo_eliminacion = "Saltada por administrador"
        if admin:
            solicitud.eliminado_por = admin
        solicitud.save(
            update_fields=[
                "estado_solicitud",
                "fecha_inicio_reproduccion",
                "fecha_finalizacion",
                "motivo_eliminacion",
                "eliminado_por",
            ]
        )
        self.reordenar_cola()
        payload = self.solicitud_to_dict(solicitud)
        self.emitir_evento("cancion_reproducida", payload)
        self.emitir_evento("historial_musical_actualizado", payload)
        self.sincronizar_reproduccion()
        return solicitud

    def marcar_reproducida(self, solicitud_id, *, admin=None):
        solicitud = self.historial_queryset().filter(pk=solicitud_id).first()
        if not solicitud:
            return None
        ahora = timezone.now()
        solicitud.estado_solicitud = "reproducida"
        solicitud.fecha_inicio_reproduccion = solicitud.fecha_inicio_reproduccion or ahora
        solicitud.fecha_finalizacion = ahora
        solicitud.motivo_eliminacion = ""
        if admin:
            solicitud.eliminado_por = admin
        solicitud.save(
            update_fields=[
                "estado_solicitud",
                "fecha_inicio_reproduccion",
                "fecha_finalizacion",
                "motivo_eliminacion",
                "eliminado_por",
            ]
        )
        self.reordenar_cola()
        payload = self.solicitud_to_dict(solicitud)
        self.emitir_evento("cancion_reproducida", payload)
        self.emitir_evento("historial_musical_actualizado", payload)
        self.sincronizar_reproduccion()
        return solicitud

    def reordenar_cola(self):
        activos = list(
            self.cola_queryset().order_by(
                "estado_solicitud",
                "posicion_orden",
                "id_solicitud",
            )
        )
        changed = False
        posicion = 1
        for item in activos:
            new_position = 1 if item.estado_solicitud == "reproduciendo" else posicion + (0 if posicion == 1 and any(x.estado_solicitud == "reproduciendo" for x in activos) else 0)
            if item.estado_solicitud == "reproduciendo":
                new_position = 1
            else:
                reproducion_activa = any(x.estado_solicitud == "reproduciendo" for x in activos)
                if reproducion_activa:
                    pendientes_antes = [x for x in activos if x.estado_solicitud == "pendiente"]
                    idx = pendientes_antes.index(item) if item in pendientes_antes else 0
                    new_position = idx + 2
                else:
                    pendientes_antes = [x for x in activos if x.estado_solicitud == "pendiente"]
                    idx = pendientes_antes.index(item) if item in pendientes_antes else 0
                    new_position = idx + 1
            if item.posicion_orden != new_position:
                item.posicion_orden = new_position
                changed = True
        if changed:
            SolicitudMusica.objects.bulk_update(activos, ["posicion_orden"])

    def sincronizar_reproduccion(self):
        self.asegurar_esquema()
        reproduciendo_qs = self.cola_queryset().filter(estado_solicitud="reproduciendo").order_by(
            "fecha_inicio_reproduccion", "posicion_orden", "id_solicitud"
        )
        reproduciendo_list = list(reproduciendo_qs[:10])
        if len(reproduciendo_list) > 1:
            principal = reproduciendo_list[0]
            extras = reproduciendo_list[1:]
            for extra in extras:
                extra.estado_solicitud = "pendiente"
                extra.fecha_inicio_reproduccion = None
            SolicitudMusica.objects.bulk_update(extras, ["estado_solicitud", "fecha_inicio_reproduccion"])

        reproduciendo = (
            self.cola_queryset()
            .filter(estado_solicitud="reproduciendo")
            .order_by("fecha_inicio_reproduccion", "posicion_orden", "id_solicitud")
            .first()
        )
        ahora = timezone.now()
        changed = False

        if reproduciendo:
            fin_programado = (reproduciendo.fecha_inicio_reproduccion or ahora) + timedelta(
                seconds=self.duracion_para_solicitud(reproduciendo)
            )
            if fin_programado <= ahora:
                reproduciendo.estado_solicitud = "reproducida"
                reproduciendo.fecha_finalizacion = ahora
                reproduciendo.save(update_fields=["estado_solicitud", "fecha_finalizacion"])
                payload = self.solicitud_to_dict(reproduciendo)
                self.emitir_evento("cancion_reproducida", payload)
                self.emitir_evento("historial_musical_actualizado", payload)
                reproduciendo = None
                changed = True

        if not reproduciendo:
            siguiente = (
                self.cola_queryset()
                .filter(estado_solicitud="pendiente")
                .order_by("posicion_orden", "fecha_solicitud", "id_solicitud")
                .first()
            )
            if siguiente:
                siguiente.estado_solicitud = "reproduciendo"
                siguiente.fecha_inicio_reproduccion = ahora
                if not siguiente.posicion_orden or siguiente.posicion_orden != 1:
                    siguiente.posicion_orden = 1
                siguiente.save(update_fields=["estado_solicitud", "fecha_inicio_reproduccion", "posicion_orden"])
                payload = self.solicitud_to_dict(siguiente)
                self.emitir_evento("cancion_reproduciendo", payload)
                changed = True

        if changed:
            self.reordenar_cola()
            self.emitir_evento("orden_cola_actualizado", self.snapshot())

    def snapshot(self):
        self.sincronizar_reproduccion_guardada()
        cola = [self.solicitud_to_dict(item) for item in self.cola_queryset().order_by("posicion_orden", "id_solicitud")]
        actual = next((item for item in cola if item.get("estado_solicitud") == "reproduciendo"), None)
        return {
            "actual": actual,
            "cola": cola,
            "total_activas": len(cola),
        }

    def sincronizar_reproduccion_guardada(self):
        lock_key = "bongusto.music.sync.lock"
        if not cache.add(lock_key, "1", timeout=10):
            return
        try:
            self.sincronizar_reproduccion()
        finally:
            cache.delete(lock_key)

    def solicitud_to_dict(self, solicitud):
        mesa = solicitud.mesa
        usuario = solicitud.id_usuario
        duracion = self.duracion_para_solicitud(solicitud)
        remaining = None
        if solicitud.estado_solicitud == "reproduciendo" and solicitud.fecha_inicio_reproduccion:
            fin = solicitud.fecha_inicio_reproduccion + timedelta(seconds=duracion)
            remaining = max(0, int((fin - timezone.now()).total_seconds()))
        return {
            "id_solicitud": solicitud.id_solicitud,
            "id_musica": solicitud.id_musica_id,
            "cancion": solicitud.cancion_final,
            "artista": solicitud.artista_final,
            "cliente_id": usuario.id_usuario if usuario else None,
            "cliente_nombre": usuario.nombre_completo() if usuario else "",
            "mesa_id": mesa.id if mesa else None,
            "mesa_label": mesa.etiqueta if mesa else "",
            "estado_solicitud": solicitud.estado_solicitud or "pendiente",
            "posicion_orden": solicitud.posicion_orden or 0,
            "duracion_segundos": duracion,
            "segundos_restantes": remaining,
            "fecha_solicitud": solicitud.fecha_solicitud.isoformat() if solicitud.fecha_solicitud else "",
            "fecha_inicio_reproduccion": solicitud.fecha_inicio_reproduccion.isoformat() if solicitud.fecha_inicio_reproduccion else "",
            "fecha_finalizacion": solicitud.fecha_finalizacion.isoformat() if solicitud.fecha_finalizacion else "",
            "eliminado_por": solicitud.eliminado_por.nombre_completo() if solicitud.eliminado_por else "",
            "motivo_eliminacion": solicitud.motivo_eliminacion or "",
            "musica": {
                "id_musica": solicitud.id_musica_id,
                "nombre_musica": solicitud.cancion_final,
                "artista_musica": solicitud.artista_final,
                "duracion_musica": duracion,
            },
        }

    def resumen_pdf(self, *, fecha=None, periodo=None):
        historial = self.historial(fecha=fecha, periodo=periodo)
        queryset = self.historial_queryset()
        today = timezone.localdate()
        if fecha == "hoy":
            queryset = queryset.filter(fecha_solicitud__date=today)
        elif periodo == "semanal":
            queryset = queryset.filter(fecha_solicitud__date__gte=today - timedelta(days=6))
        elif periodo == "mensual":
            queryset = queryset.filter(fecha_solicitud__date__gte=today - timedelta(days=29))

        ranking = list(
            queryset.values("cancion", "artista")
            .annotate(total=Count("id_solicitud"))
            .order_by("-total", "cancion")[:10]
        )
        return {
            "historial": historial,
            "ranking": ranking,
            "totales_por_estado": {
                item["estado_solicitud"]: item["total"]
                for item in queryset.values("estado_solicitud").annotate(total=Count("id_solicitud"))
            },
        }

    def emitir_evento(self, evento, payload):
        emitir_evento_operacion(f"musica_{evento}", payload)
        from bongusto.modules.musica.realtime import emitir_evento_musica

        emitir_evento_musica(evento, payload)


__all__ = ["MusicaService", "Musica", "Usuario", "SolicitudMusica"]
