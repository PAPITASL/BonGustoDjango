"""Configuracion Django del modulo `usuarios`: usuarios del sistema y clientes API."""

# ===== Importaciones | Dependencias que este archivo necesita para funcionar dentro del modulo. =====
from django.apps import AppConfig



# ===== Clase `UsuariosConfig` | Modulo `usuarios` | Esta clase agrupa logica relacionada con usuarios y clientes. =====
class UsuariosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bongusto.modules.usuarios"
    label = "modules_usuarios"
    verbose_name = "Modulo Usuarios"
