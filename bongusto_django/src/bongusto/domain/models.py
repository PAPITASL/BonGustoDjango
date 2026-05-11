"""
Modelos principales de BonGusto.

Aquí se crean las tablas principales del sistema.
Cada clase representa una tabla de la base de datos.
"""

from django.core.exceptions import ValidationError
from django.db import models


# ==================================================
# ROLES Y PERMISOS
# ==================================================

# Guarda los roles del sistema
# Ejemplo: administrador, cliente, trabajador, mesero
class Rol(models.Model):

    # Id principal del rol
    id_rol = models.AutoField(primary_key=True)

    # Nombre del rol
    nombre_rol = models.CharField(max_length=50)

    class Meta:
        # Nombre de la tabla en la base de datos
        db_table = "roles"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

    def clean(self):
        self.nombre_rol = (self.nombre_rol or "").strip()
        if not self.nombre_rol:
            raise ValidationError({"nombre_rol": "El nombre del rol es obligatorio."})

        qs = Rol.objects.filter(nombre_rol__iexact=self.nombre_rol)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({"nombre_rol": "Ya existe un rol con ese nombre."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    # Esto hace que se vea mejor cuando se muestre el rol
    def __str__(self):
        return self.nombre_rol


# Guarda los permisos del sistema
# Ejemplo: crear, editar, eliminar, ver
class Permiso(models.Model):

    # Id principal del permiso
    id_permiso = models.AutoField(primary_key=True)

    # Nombre del permiso
    nombre_permiso = models.CharField(max_length=100)

    # Descripción opcional
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "permisos"
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"

    def clean(self):
        self.nombre_permiso = (self.nombre_permiso or "").strip()
        if not self.nombre_permiso:
            raise ValidationError({"nombre_permiso": "El nombre del permiso es obligatorio."})

        qs = Permiso.objects.filter(nombre_permiso__iexact=self.nombre_permiso)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({"nombre_permiso": "Ya existe un permiso con ese nombre."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    # Muestra el nombre del permiso
    def __str__(self):
        return self.nombre_permiso


# Une roles con permisos
# Aqui se define qué permisos tiene cada rol
class RolPermiso(models.Model):

    # Relación con rol
    id_rol = models.ForeignKey(
        Rol,
        db_column="id_rol",
        on_delete=models.CASCADE
    )

    # Relación con permiso
    id_permiso = models.ForeignKey(
        Permiso,
        db_column="id_permiso",
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = "rol_permisos"

        # Evita repetir el mismo rol con el mismo permiso
        unique_together = (("id_rol", "id_permiso"),)


# ==================================================
# USUARIOS
# ==================================================

# Guarda los usuarios del sistema
class Usuario(models.Model):

    # Tipos de usuario permitidos
    TIPO_CHOICES = [
        ("cliente", "Cliente"),
        ("administrador", "Administrador"),
        ("trabajador", "Trabajador"),
        ("mesero", "Mesero"),
    ]

    # Id principal del usuario
    id_usuario = models.AutoField(primary_key=True)

    # Datos básicos
    nombre = models.CharField(max_length=50, null=True, blank=True)
    apellido = models.CharField(max_length=50, null=True, blank=True)
    correo = models.CharField(max_length=100, null=True, blank=True)
    clave = models.CharField(max_length=255, null=True, blank=True)

    # Tipo de usuario
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        null=True,
        blank=True
    )

    # Relación con rol
    # Si se elimina el rol, este campo queda vacío
    id_rol = models.ForeignKey(
        Rol,
        db_column="id_rol",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Estado del usuario
    estado = models.CharField(max_length=20, default="Activo")

    # Teléfono
    telefono = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def clean(self):
        self.correo = (self.correo or "").strip().lower()
        if self.correo:
            qs = Usuario.objects.filter(correo__iexact=self.correo)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({"correo": "Ya existe un usuario con ese correo."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    # Muestra el nombre del usuario
    def __str__(self):
        return f"{self.nombre} {self.apellido or ''}".strip()

    # Devuelve nombre completo
    def nombre_completo(self):
        return f"{self.nombre or ''} {self.apellido or ''}".strip()

    # Devuelve el nombre del rol si tiene uno
    def get_rol_nombre(self):
        if self.id_rol:
            return self.id_rol.nombre_rol
        return "Sin rol"


# ==================================================
# BITÁCORA
# ==================================================

# Guarda el historial de acciones del sistema
class Bitacora(models.Model):

    # Id principal del registro
    id_log = models.AutoField(primary_key=True)

    # Usuario relacionado
    # Puede quedar vacío si lo hizo el sistema
    id_usuario = models.ForeignKey(
        Usuario,
        db_column="id_usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Acción realizada
    accion = models.TextField(null=True, blank=True)

    # Fecha y hora de la acción
    fecha_accion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "bitacora"
        verbose_name = "Bitácora"
        verbose_name_plural = "Bitácoras"

    # Muestra un resumen del log
    def __str__(self):
        return f"Log {self.id_log} - {self.accion}"


# ==================================================
# MENÚ Y CATEGORÍAS
# ==================================================

# Guarda los menús del sistema
class Menu(models.Model):

    # Id principal del menú
    id_menu = models.AutoField(primary_key=True)

    # Nombre y descripción
    nombre_menu = models.CharField(max_length=300, null=True, blank=True)
    descripcion_menu = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = "menu"
        verbose_name = "Menú"
        verbose_name_plural = "Menús"

    def clean(self):
        self.nombre_menu = (self.nombre_menu or "").strip()
        if not self.nombre_menu:
            raise ValidationError({"nombre_menu": "El nombre del menu es obligatorio."})

        qs = Menu.objects.filter(nombre_menu__iexact=self.nombre_menu)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({"nombre_menu": "Ya existe un menu con ese nombre."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    # Muestra el menú con un texto entendible
    def __str__(self):
        return self.nombre_menu or f"Menú {self.id_menu}"

    # Alias para usar el nombre más fácil
    @property
    def item(self):
        return self.nombre_menu

    @property
    def descripcion(self):
        return self.descripcion_menu


# Guarda las categorías de productos
class Categoria(models.Model):

    # Id principal de la categoría
    id_cate = models.AutoField(primary_key=True)

    # Nombre de la categoría
    nombre_cate = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "categorias"
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def clean(self):
        self.nombre_cate = (self.nombre_cate or "").strip()
        if not self.nombre_cate:
            raise ValidationError({"nombre_cate": "El nombre de la categoria es obligatorio."})

        qs = Categoria.objects.filter(nombre_cate__iexact=self.nombre_cate)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({"nombre_cate": "Ya existe una categoria con ese nombre."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    # Muestra el nombre de la categoría
    def __str__(self):
        return self.nombre_cate or f"Categoría {self.id_cate}"

    # Alias para usar el nombre más fácil
    @property
    def nombre(self):
        return self.nombre_cate


# ==================================================
# PRODUCTOS
# ==================================================

# Guarda los productos del sistema
class Producto(models.Model):

    # Estados del producto
    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    # Id principal del producto
    id_producto = models.AutoField(primary_key=True)

    # Datos del producto
    nombre_producto = models.CharField(max_length=300, null=True, blank=True)
    precio_producto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    descripcion_producto = models.CharField(max_length=300, null=True, blank=True)

    # Relación con menú
    id_menu = models.ForeignKey(
        Menu,
        db_column="id_menu",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Relación con categoría
    id_cate = models.ForeignKey(
        Categoria,
        db_column="id_cate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Id del restaurante
    id_res = models.IntegerField(null=True, blank=True)

    # Estado del producto
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default="activo",
        null=True,
        blank=True
    )

    class Meta:
        db_table = "productos"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def clean(self):
        self.nombre_producto = (self.nombre_producto or "").strip()
        self.descripcion_producto = (self.descripcion_producto or "").strip()

        if not self.nombre_producto:
            raise ValidationError({"nombre_producto": "El nombre del producto es obligatorio."})
        if self.precio_producto is None:
            raise ValidationError({"precio_producto": "El precio del producto es obligatorio."})

        qs = Producto.objects.filter(nombre_producto__iexact=self.nombre_producto)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({"nombre_producto": "Ya existe un producto con ese nombre."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    # Muestra el nombre del producto
    def __str__(self):
        return self.nombre_producto or f"Producto {self.id_producto}"

    # Alias para usar datos más fácil
    @property
    def nombre(self):
        return self.nombre_producto

    @property
    def precio(self):
        return self.precio_producto

    @property
    def descripcion(self):
        return self.descripcion_producto

    @property
    def menu(self):
        return self.id_menu

    @property
    def categoria(self):
        return self.id_cate


# ==================================================
# MÚSICA Y SOLICITUDES
# ==================================================

# Guarda las canciones del sistema
class Musica(models.Model):

    # Id principal de la canción
    id_musica = models.AutoField(primary_key=True)

    # Datos de la canción
    nombre_musica = models.CharField(max_length=100, null=True, blank=True)
    artista_musica = models.CharField(max_length=100, null=True, blank=True)
    duracion_musica = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "musica"
        verbose_name = "Música"
        verbose_name_plural = "Músicas"

    def clean(self):
        self.nombre_musica = (self.nombre_musica or "").strip()
        self.artista_musica = (self.artista_musica or "").strip()

        if not self.nombre_musica:
            raise ValidationError({"nombre_musica": "El nombre de la cancion es obligatorio."})
        if not self.artista_musica:
            raise ValidationError({"artista_musica": "El artista de la cancion es obligatorio."})

        qs = Musica.objects.filter(
            nombre_musica__iexact=self.nombre_musica,
            artista_musica__iexact=self.artista_musica,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({"nombre_musica": "Ya existe una cancion con ese nombre y artista."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    # Muestra nombre y artista
    def __str__(self):
        return f"{self.nombre_musica} - {self.artista_musica}"

    # Alias para usar datos más fácil
    @property
    def titulo(self):
        return self.nombre_musica

    @property
    def artista(self):
        return self.artista_musica

    @property
    def duracion(self):
        return self.duracion_musica


# Guarda las solicitudes de música
class SolicitudMusica(models.Model):
  
    # Estados de la solicitud
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("reproduciendo", "Reproduciendo"),
        ("reproducida", "Reproducida"),
        ("eliminada", "Eliminada"),
    ]

    # Id principal de la solicitud
    id_solicitud = models.AutoField(primary_key=True)

    # Usuario que pidió la canción
    id_usuario = models.ForeignKey(
        Usuario,
        db_column="id_usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Canción solicitada
    id_musica = models.ForeignKey(
        Musica,
        db_column="id_musica",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    mesa = models.ForeignKey(
        "modules_mesas.Mesa",
        db_column="mesa_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes_musica",
        db_constraint=False,
    )

    cancion = models.CharField(max_length=150, null=True, blank=True)
    artista = models.CharField(max_length=150, null=True, blank=True)
    posicion_orden = models.PositiveIntegerField(null=True, blank=True)
    duracion_segundos = models.PositiveIntegerField(null=True, blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_inicio_reproduccion = models.DateTimeField(null=True, blank=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    eliminado_por = models.ForeignKey(
        Usuario,
        db_column="eliminado_por_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes_musica_eliminadas",
        db_constraint=False,
    )
    motivo_eliminacion = models.TextField(null=True, blank=True)

    # Restaurante relacionado
    id_res = models.IntegerField(null=True, blank=True)

    # Estado de la solicitud
    estado_solicitud = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="pendiente",
        null=True,
        blank=True
    )

    class Meta:
        db_table = "solicitud_musica"
        verbose_name = "Solicitud de Música"
        verbose_name_plural = "Solicitudes de Música"

    # Muestra la solicitud de forma simple
    def __str__(self):
        return f"Solicitud {self.id_solicitud}"

    @property
    def cancion_final(self):
        if self.cancion:
            return self.cancion
        if self.id_musica:
            return self.id_musica.nombre_musica or ""
        return ""

    @property
    def artista_final(self):
        if self.artista:
            return self.artista
        if self.id_musica:
            return self.id_musica.artista_musica or ""
        return ""


# ==================================================
# RESERVAS
# ==================================================

# Guarda las reservas del sistema
class Reserva(models.Model):

    # Estados posibles de una reserva
    ESTADO_CHOICES = [
        ("activa", "Activa"),
        ("cancelada", "Cancelada"),
        ("finalizada", "Finalizada"),
    ]

    # Id principal de la reserva
    id_reser = models.AutoField(primary_key=True)

    # Usuario relacionado
    id_usuario = models.ForeignKey(
        Usuario,
        db_column="id_usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Datos de la reserva
    nombre_evento = models.CharField(max_length=120, null=True, blank=True)
    id_res = models.IntegerField(null=True, blank=True)
    mesa = models.ForeignKey(
        "modules_mesas.Mesa",
        db_column="mesa_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservas",
        db_constraint=False,
    )
    fecha_reser = models.DateField(null=True, blank=True)
    estado_reser = models.CharField(max_length=12, choices=ESTADO_CHOICES, null=True, blank=True)
    hora_reser = models.CharField(max_length=5, null=True, blank=True)
    detalle_evento = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = "reservas"
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    # Muestra un resumen de la reserva
    def __str__(self):
        return f"Reserva {self.id_reser} - {self.fecha_reser}"

    @property
    def fecha(self):
        return self.fecha_reser

    @property
    def estado(self):
        return self.estado_reser

    @property
    def hora(self):
        return self.hora_reser

    # Devuelve quién sería el responsable del evento
    @property
    def responsable_evento(self):
        if self.nombre_evento:
            return self.nombre_evento
        if self.id_usuario:
            return self.id_usuario.nombre_completo()
        return "Sin responsable"


# ==================================================
# PEDIDOS
# ==================================================

# Guarda las calificaciones que dejan los clientes
class CalificacionCliente(models.Model):

    # Id principal de la calificación
    id_calificacion = models.AutoField(primary_key=True)

    # Usuario que calificó
    id_usuario = models.ForeignKey(
        Usuario,
        db_column="id_usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_constraint=False
    )

    # Pedido relacionado
    # Va en comillas porque PedidoEncabezado se declara después
    id_pedido = models.ForeignKey(
        "PedidoEncabezado",
        db_column="id_pedido",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_constraint=False
    )

    # Calificaciones del cliente
    calificacion_comida = models.PositiveSmallIntegerField(null=True, blank=True)
    calificacion_servicio = models.PositiveSmallIntegerField(null=True, blank=True)
    calificacion_ambiente = models.PositiveSmallIntegerField(null=True, blank=True)

    # Comentario del cliente
    observaciones = models.TextField(null=True, blank=True)

    # Fecha automática cuando se crea
    fecha_calificacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = "calificaciones_clientes"
        verbose_name = "Calificacion"
        verbose_name_plural = "Calificaciones"
        constraints = [
            models.UniqueConstraint(
                fields=["id_pedido"],
                name="calificaciones_unica_por_pedido",
            )
        ]

    # Muestra la calificación de forma simple
    def __str__(self):
        return f"Calificacion {self.id_calificacion}"

    # Calcula el promedio de las 3 calificaciones
    @property
    def promedio(self):
        valores = [
            int(self.calificacion_comida or 0),
            int(self.calificacion_servicio or 0),
            int(self.calificacion_ambiente or 0),
        ]

        # Solo toma valores mayores a 0
        valores = [valor for valor in valores if valor > 0]

        if not valores:
            return 0

        return round(sum(valores) / len(valores), 1)


# Guarda la cabecera del pedido
class PedidoEncabezado(models.Model):

    # Id principal del pedido
    id_pedido = models.AutoField(primary_key=True)

    ESTADO_CHOICES = [
        ("abierto", "Abierto"),
        ("en_preparacion", "En preparacion"),
        ("listo_para_recoger", "Listo para recoger"),
        ("entregado", "Entregado"),
        ("pagado", "Pagado"),
        ("finalizado", "Finalizado"),
    ]
    TIPO_CHOICES = [
        ("restaurante", "Restaurante"),
        ("para_llevar", "Para llevar"),
    ]

    # Usuario que hizo el pedido
    id_usuario = models.ForeignKey(
        Usuario,
        db_column="id_usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Datos generales del pedido
    id_restaurante = models.IntegerField(null=True, blank=True)
    tipo_pedido = models.CharField(max_length=20, choices=TIPO_CHOICES, default="restaurante")
    mesa = models.ForeignKey(
        "modules_mesas.Mesa",
        db_column="mesa_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos",
        db_constraint=False,
    )
    fecha_pedido = models.DateField(null=True, blank=True)
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado_pedido = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="abierto")
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "pedido_encabezado"
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    # Muestra el pedido con su total
    def __str__(self):
        return f"Pedido {self.id_pedido} - ${self.total_pedido}"


# Guarda el detalle del pedido
# Aqui van los productos de cada pedido
class PedidoDetalle(models.Model):

    # Id principal del detalle
    id_detalle = models.AutoField(primary_key=True)

    # Relación con el pedido
    id_pedido = models.ForeignKey(
        PedidoEncabezado,
        db_column="id_pedido",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Datos del detalle
    id_producto = models.BigIntegerField(null=True, blank=True)
    cantidad = models.IntegerField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "pedido_detalle"
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedido"


class SolicitudPago(models.Model):
    """Registra la intencion de pago del cliente sin procesar dinero."""

    id_solicitud_pago = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey(
        PedidoEncabezado,
        db_column="id_pedido",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_constraint=False,
    )
    id_usuario = models.ForeignKey(
        Usuario,
        db_column="id_usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes_pago_cliente",
        db_constraint=False,
    )
    mesa = models.ForeignKey(
        "modules_mesas.Mesa",
        db_column="mesa_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes_pago",
        db_constraint=False,
    )
    metodo_pago = models.CharField(max_length=40)
    estado = models.CharField(max_length=30, default="pendiente")
    atendido_por = models.ForeignKey(
        Usuario,
        db_column="id_mesero_atendio",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes_pago_atendidas",
        db_constraint=False,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    finalizado_en = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "solicitudes_pago"
        verbose_name = "Solicitud de pago"
        verbose_name_plural = "Solicitudes de pago"
        ordering = ["-fecha_creacion", "-id_solicitud_pago"]

    def __str__(self):
        return f"Solicitud pago {self.id_solicitud_pago} - Mesa {self.mesa_id}"


# ==================================================
# CHAT
# ==================================================

# Guarda los mensajes del chat
class MensajeChat(models.Model):

    # Id principal del mensaje
    id = models.AutoField(primary_key=True)

    # Datos del mensaje
    remitente = models.CharField(max_length=50)
    destinatario = models.CharField(max_length=50)
    mensaje = models.TextField()

    # Fecha automática cuando se crea
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mensajes_chat"
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"

        # Ordena los mensajes por fecha
        ordering = ["fecha"]

    # Muestra un resumen corto del mensaje
    def __str__(self):
        return f"{self.remitente} → {self.destinatario}: {self.mensaje[:40]}"


# ==================================================
# NOTIFICACIONES
# ==================================================

class NotificacionCliente(models.Model):

    # Id principal de la notificacion
    id_notificacion = models.AutoField(primary_key=True)

    # Cliente que recibira la notificacion
    id_usuario = models.ForeignKey(
        Usuario,
        db_column="id_usuario",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Contenido principal
    titulo = models.CharField(max_length=120)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=30, default="general")

    # Estado de lectura
    leida = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notificaciones_clientes"
        verbose_name = "Notificacion"
        verbose_name_plural = "Notificaciones"
        ordering = ["-fecha_envio", "-id_notificacion"]

    def __str__(self):
        destino = self.id_usuario.nombre_completo() if self.id_usuario else "Sin destinatario"
        return f"{self.titulo} -> {destino}"
