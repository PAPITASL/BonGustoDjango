"""Configuracion Django del modulo `pedidos`: manejo de encabezados y detalle de pedidos del sistema."""


# ===== Importaciones | Dependencias necesarias para el funcionamiento del modulo `pedidos`. =====
from django.apps import AppConfig



# ===== Clase `PedidosConfig` | Modulo `pedidos` | Configuracion principal del modulo dentro del proyecto Django. =====
class PedidosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bongusto.modules.pedidos"
    label = "modules_pedidos"
    verbose_name = "Modulo Pedidos"
