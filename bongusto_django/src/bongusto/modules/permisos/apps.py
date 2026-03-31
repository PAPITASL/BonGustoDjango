"""Configuracion Django del modulo `permisos`: gestion del catalogo de permisos del sistema."""

# ===== Importaciones | Dependencias que este archivo necesita para funcionar dentro del modulo. =====
from django.apps import AppConfig



# ===== Clase `PermisosConfig` | Modulo `permisos` | Agrupa la configuracion base del modulo de permisos. =====
class PermisosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bongusto.modules.permisos"
    label = "modules_permisos"
    verbose_name = "Modulo Permisos"
