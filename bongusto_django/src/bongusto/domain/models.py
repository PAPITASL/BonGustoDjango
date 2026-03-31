"""
Modelos principales de BonGusto.

Aquí se crean las tablas del sistema con Django.
Cada clase representa una tabla de la base de datos.
"""

from django.db import models


# ==================================================
# ROLES Y PERMISOS
# ==================================================

# Este modelo guarda los roles del sistema
# Por ejemplo: administrador, cliente, trabajador, etc.
class Rol(models.Model):

    # Este es el id principal y se genera solo
    id_rol = models.AutoField(primary_key=True)

    # Aquí se guarda el nombre del rol
    nombre_rol = models.CharField(max_length=50)

    class Meta:
        # Nombre real de la tabla en la base de datos
        db_table = "roles"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

    # Esto sirve para que al mostrar el objeto salga algo entendible
    def __str__(self):
        return self.nombre_rol


# Este modelo guarda los permisos
# Por ejemplo: crear, editar, eliminar, ver, etc.
class Permiso(models.Model):

    # Id principal
    id_permiso = models.AutoField(primary_key=True)

    # Nombre del permiso
    nombre_permiso = models.CharField(max_length=100)

    # Descripción opcional del permiso
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "permisos"
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"

    def __str__(self):
        return self.nombre_permiso


# Este modelo une roles con permisos
# O sea, dice qué permisos tiene cada rol
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

        # Esto evita que se repita el mismo rol con el mismo permiso
        unique_together = (("id_rol", "id_permiso"),)


# ==================================================
# USUARIOS
# ==================================================

# Este modelo guarda los usuarios del sistema
class Usuario(models.Model):

    # Estas son las opciones posibles del tipo de usuario
    TIPO_CHOICES = [
        ("cliente", "Cliente"),
        ("administrador", "Administrador"),
        ("trabajador", "Trabajador"),
        ("mesero", "Mesero"),
    ]

    # Id principal
    id_usuario = models.AutoField(primary_key=True)

    # Datos básicos del usuario
    nombre = models.CharField(max_length=50, null=True, blank=True)
    apellido = models.CharField(max_length=50, null=True, blank=True)
    correo = models.CharField(max_length=100, null=True, blank=True)
    clave = models.CharField(max_length=255, null=True, blank=True)

    # Tipo de usuario según las opciones de arriba
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        null=True,
        blank=True
    )

    # Relación con rol
    # Si el rol se borra, este campo queda en null
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

    def __str__(self):
        return f"{self.nombre} {self.apellido or ''}".strip()

    # Esto devuelve el nombre completo del usuario
    def nombre_completo(self):
        return f"{self.nombre or ''} {self.apellido or ''}".strip()

    # Esto devuelve el nombre del rol si existe
    def get_rol_nombre(self):
        if self.id_rol:
            return self.id_rol.nombre_rol
        return "Sin rol"


# ==================================================
# BITÁCORA
# ==================================================

# Este modelo guarda el historial de acciones del sistema
class Bitacora(models.Model):

    # Id principal del registro de bitácora
    id_log = models.AutoField(primary_key=True)

    # Relación con usuario
    # Puede quedar vacío si la acción la hizo el sistema
    id_usuario = models.ForeignKey(
        Usuario,
        db_column="id_usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Aquí se guarda lo que pasó
    accion = models.TextField(null=True, blank=True)

    # Fecha y hora del movimiento
    fecha_accion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "bitacora"
        verbose_name = "Bitácora"
        verbose_name_plural = "Bitácoras"

    def __str__(self):
        return f"Log {self.id_log} - {self.accion}"


# ==================================================
# MENÚ Y CATEGORÍAS
# ==================================================

# Este modelo guarda los menús
class Menu(models.Model):

    # Id principal
    id_menu = models.AutoField(primary_key=True)

    # Nombre y descripción del menú
    nombre_menu = models.CharField(max_length=300, null=True, blank=True)
    descripcion_menu = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = "menu"
        verbose_name = "Menú"
        verbose_name_plural = "Menús"

    def __str__(self):
        return self.nombre_menu or f"Menú {self.id_menu}"

    # Estos property sirven como alias
    # O sea, otra forma de llamar el mismo dato
    @property
    def item(self):
        return self.nombre_menu

    @property
    def descripcion(self):
        return self.descripcion_menu


# Este modelo guarda las categorías
class Categoria(models.Model):

    # Id principal
    id_cate = models.AutoField(primary_key=True)

    # Nombre de la categoría
    nombre_cate = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "categorias"
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre_cate or f"Categoría {self.id_cate}"

    @property
    def nombre(self):
        return self.nombre_cate


# ==================================================
# PRODUCTOS
# ==================================================

# Este modelo guarda los productos del sistema
class Producto(models.Model):

    # Opciones del estado del producto
    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    # Id principal
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

    def __str__(self):
        return self.nombre_producto or f"Producto {self.id_producto}"

    # Alias que ayudan en templates o en otras partes del sistema
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

# Este modelo guarda las canciones
class Musica(models.Model):

    # Id principal
    id_musica = models.AutoField(primary_key=True)

    # Datos de la canción
    nombre_musica = models.CharField(max_length=100, null=True, blank=True)
    artista_musica = models.CharField(max_length=100, null=True, blank=True)
    duracion_musica = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "musica"
        verbose_name = "Música"
        verbose_name_plural = "Músicas"

    def __str__(self):
        return f"{self.nombre_musica} - {self.artista_musica}"

    # Alias
    @property
    def titulo(self):
        return self.nombre_musica

    @property
    def artista(self):
        return self.artista_musica

    @property
    def duracion(self):
        return self.duracion_musica


# Este modelo guarda las solicitudes de música
class SolicitudMusica(models.Model):

    # Posibles estados de la solicitud
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
    ]

    # Id principal
    id_solicitud = models.AutoField(primary_key=True)

    # Usuario que hizo la solicitud
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

    # Restaurante relacionado
    id_res = models.IntegerField(null=True, blank=True)

    # Estado de la solicitud
    estado_solicitud = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        null=True,
        blank=True
    )

    class Meta:
        db_table = "solicitud_musica"
        verbose_name = "Solicitud de Música"
        verbose_name_plural = "Solicitudes de Música"

    def __str__(self):
        return f"Solicitud {self.id_solicitud}"


# ==================================================
# RESERVAS
# ==================================================

# Este modelo guarda las reservas
class Reserva(models.Model):

    # Posibles estados de la reserva
    ESTADO_CHOICES = [
        ("activa", "Activa"),
        ("cancelada", "Cancelada"),
        ("finalizada", "Finalizada"),
    ]

    # Id principal
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
    fecha_reser = models.DateField(null=True, blank=True)
    estado_reser = models.CharField(max_length=12, choices=ESTADO_CHOICES, null=True, blank=True)
    hora_reser = models.CharField(max_length=5, null=True, blank=True)
    detalle_evento = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = "reservas"
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

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

    # Esto devuelve quién sería el responsable del evento
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

# Este modelo guarda las calificaciones del cliente
class CalificacionCliente(models.Model):

    # Id principal
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
    # Va entre comillas porque este modelo se usa antes de declarar PedidoEncabezado
    id_pedido = models.ForeignKey(
        "PedidoEncabezado",
        db_column="id_pedido",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_constraint=False
    )

    # Calificaciones
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

    def __str__(self):
        return f"Calificacion {self.id_calificacion}"

    # Esto calcula el promedio de las 3 calificaciones
    @property
    def promedio(self):
        valores = [
            int(self.calificacion_comida or 0),
            int(self.calificacion_servicio or 0),
            int(self.calificacion_ambiente or 0),
        ]

        # Solo toma los valores mayores a 0
        valores = [valor for valor in valores if valor > 0]

        if not valores:
            return 0

        return round(sum(valores) / len(valores), 1)


# Este modelo guarda la cabecera del pedido
class PedidoEncabezado(models.Model):

    # Id principal
    id_pedido = models.AutoField(primary_key=True)

    # Usuario que hizo el pedido
    id_usuario = models.ForeignKey(
        Usuario,
        db_column="id_usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Datos del pedido
    id_restaurante = models.IntegerField(null=True, blank=True)
    fecha_pedido = models.DateField(null=True, blank=True)
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "pedido_encabezado"
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido {self.id_pedido} - ${self.total_pedido}"


# Este modelo guarda el detalle del pedido
# O sea, los productos individuales de cada pedido
class PedidoDetalle(models.Model):

    # Id principal
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


# ==================================================
# CHAT
# ==================================================

# Este modelo guarda los mensajes del chat
class MensajeChat(models.Model):

    # Id principal
    id = models.AutoField(primary_key=True)

    # Datos del mensaje
    remitente = models.CharField(max_length=50)
    destinatario = models.CharField(max_length=50)
    mensaje = models.TextField()

    # Se guarda automáticamente la fecha cuando se crea
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mensajes_chat"
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"

        # Esto hace que salgan ordenados por fecha
        ordering = ["fecha"]

    def __str__(self):
        return f"{self.remitente} → {self.destinatario}: {self.mensaje[:40]}"