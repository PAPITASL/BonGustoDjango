"""Configuracion Django del modulo `perfil`: manejo del perfil del usuario autenticado."""

# ===== Importaciones | Dependencias que este archivo necesita para funcionar dentro del modulo. =====
from django.apps import AppConfig



# ===== Clase `PerfilConfig` | Modulo `perfil` | Agrupa la configuracion base del modulo de perfil. =====
class PerfilConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bongusto.modules.perfil"
    label = "modules_perfil"
    verbose_name = "Modulo Perfil"
