"""Configuracion Django del modulo `roles`: 
Este modulo gestiona los roles del sistema (administrador, mesero, cliente, etc.) y su administracion interna."""


# ===== Importaciones | Dependencias que este archivo necesita para funcionar dentro del modulo. =====
from django.apps import AppConfig


# ===== Clase `RolesConfig` | Modulo `roles` | Define la configuracion principal del modulo dentro de Django. =====
class RolesConfig(AppConfig):

    # Tipo de llave primaria por defecto para los modelos del modulo
    default_auto_field = "django.db.models.BigAutoField"

    # Ruta del modulo dentro del proyecto BonGusto
    name = "bongusto.modules.roles"

    # Nombre interno unico del modulo (evita conflictos entre apps)
    label = "modules_roles"

    # Nombre visible del modulo en el panel administrativo
    verbose_name = "Modulo Roles"