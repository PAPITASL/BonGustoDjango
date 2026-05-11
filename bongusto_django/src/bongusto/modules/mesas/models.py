"""Modelos del modulo mesas."""

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from bongusto.domain.models import Usuario


class Mesa(models.Model):
    """Representa una mesa real del restaurante."""

    ESTADO_LIBRE = "libre"
    ESTADO_OCUPADA = "ocupada"
    ESTADO_ESPERANDO_PAGO = "esperando_pago"
    ESTADO_PAGADA = "pagada"
    ESTADO_EN_LIMPIEZA = "en_limpieza"
    ESTADO_BLOQUEADA = "bloqueada"

    # Alias para no romper partes legadas del proyecto.
    ESTADO_DISPONIBLE = ESTADO_LIBRE
    ESTADO_PENDIENTE_PAGO = ESTADO_ESPERANDO_PAGO
    ESTADO_INACTIVA = ESTADO_BLOQUEADA

    ESTADO_CHOICES = [
        (ESTADO_LIBRE, "Libre"),
        (ESTADO_OCUPADA, "Ocupada"),
        (ESTADO_ESPERANDO_PAGO, "Esperando pago"),
        (ESTADO_PAGADA, "Pagada"),
        (ESTADO_EN_LIMPIEZA, "En limpieza"),
        (ESTADO_BLOQUEADA, "Bloqueada"),
    ]

    id = models.AutoField(primary_key=True, db_column="id_mesa")
    numero_mesa = models.PositiveIntegerField(
        unique=True,
        validators=[MinValueValidator(1)],
    )
    nombre = models.CharField(max_length=120, null=True, blank=True)
    capacidad = models.PositiveIntegerField(default=2, validators=[MinValueValidator(1)])
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_LIBRE,
    )
    activa = models.BooleanField(default=True)
    usuario_actual = models.ForeignKey(
        Usuario,
        db_column="id_usuario_actual",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mesas_asignadas",
        db_constraint=False,
    )
    pedido_actual = models.ForeignKey(
        "domain.PedidoEncabezado",
        db_column="id_pedido_actual",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mesas_operativas",
        db_constraint=False,
    )
    mesero_asignado = models.ForeignKey(
        Usuario,
        db_column="id_mesero_asignado",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mesas_atendidas",
        db_constraint=False,
    )
    fecha_ocupacion = models.DateTimeField(null=True, blank=True)
    fecha_solicitud_pago = models.DateTimeField(null=True, blank=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_liberacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    asignado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "mesas"
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        ordering = ["numero_mesa", "id"]

    def __str__(self):
        return self.etiqueta

    @property
    def etiqueta(self):
        if self.nombre:
            return f"Mesa {self.numero_mesa} - {self.nombre}"
        return f"Mesa {self.numero_mesa}"

    @property
    def cliente_actual(self):
        return self.usuario_actual

    @property
    def created_at(self):
        return self.fecha_creacion

    @property
    def updated_at(self):
        return self.fecha_actualizacion

    def clean(self):
        if self.numero_mesa is None or int(self.numero_mesa or 0) <= 0:
            raise ValidationError({"numero_mesa": "El numero de mesa debe ser mayor a cero."})

        if self.capacidad is None or int(self.capacidad or 0) <= 0:
            raise ValidationError({"capacidad": "La capacidad debe ser mayor a cero."})

        qs = Mesa.objects.filter(numero_mesa=self.numero_mesa)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({"numero_mesa": "Ya existe una mesa con ese numero."})


__all__ = ["Mesa"]
