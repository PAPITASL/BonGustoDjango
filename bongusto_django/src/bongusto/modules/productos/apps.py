"""Configuracion Django del modulo `productos`: gestion de platos y productos del restaurante."""

# ===== Importaciones | Dependencias que este archivo necesita para funcionar dentro del modulo. =====
from django.apps import AppConfig



# ===== Clase `ProductosConfig` | Modulo `productos` | Agrupa la configuracion base del modulo de productos. =====
class ProductosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bongusto.modules.productos"
    label = "modules_productos"
    verbose_name = "Modulo Productos"